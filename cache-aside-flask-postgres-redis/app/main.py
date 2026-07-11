import json
import os
import time

import psycopg2
import redis
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

CACHE_KEY = "items:all"
CACHE_TTL_SECONDS = 60

cache = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ["REDIS_PASSWORD"],
    decode_responses=True,
)


def get_connection():
    return psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def init_db():
    # Postgres may still be starting when this container boots — retry instead of crashing.
    connection = None
    for _ in range(10):
        try:
            connection = get_connection()
            break
        except psycopg2.OperationalError:
            time.sleep(2)

    if connection is None:
        raise RuntimeError("Could not connect to PostgreSQL after 10 attempts")

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT
                )
                """
            )
    connection.close()


def wait_for_redis():
    # Redis may still be starting when this container boots — retry instead of crashing.
    for _ in range(10):
        try:
            cache.ping()
            return
        except redis.RedisError:
            time.sleep(2)

    raise RuntimeError("Could not connect to Redis after 10 attempts")


def fetch_items_from_postgres():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, description FROM items ORDER BY id")
        items = cursor.fetchall()
    connection.close()
    return items


def invalidate_cache():
    # Cache-aside: PostgreSQL is the source of truth, Redis is disposable —
    # a failure here must never break the write that triggered it.
    try:
        cache.delete(CACHE_KEY)
    except redis.RedisError:
        pass


@app.route("/")
def list_items():
    # Cache-aside read: try Redis first; on a miss (or any Redis failure),
    # fall back to PostgreSQL and repopulate the cache with a TTL as a safety
    # net alongside the active invalidation done on every write.
    try:
        cached = cache.get(CACHE_KEY)
    except redis.RedisError:
        cached = None

    if cached is not None:
        return render_template("index.html", items=json.loads(cached), served_from="cache")

    items = fetch_items_from_postgres()

    try:
        cache.setex(CACHE_KEY, CACHE_TTL_SECONDS, json.dumps(items))
    except redis.RedisError:
        pass

    return render_template("index.html", items=items, served_from="database")


@app.route("/items/new", methods=["GET", "POST"])
def create_item():
    if request.method == "POST":
        connection = get_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO items (name, description) VALUES (%s, %s)",
                    (request.form["name"], request.form["description"]),
                )
        connection.close()
        invalidate_cache()
        return redirect(url_for("list_items"))
    return render_template("form.html", item=None)


@app.route("/items/<int:item_id>/edit", methods=["GET", "POST"])
def edit_item(item_id):
    connection = get_connection()
    if request.method == "POST":
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE items SET name = %s, description = %s WHERE id = %s",
                    (request.form["name"], request.form["description"], item_id),
                )
        connection.close()
        invalidate_cache()
        return redirect(url_for("list_items"))

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, description FROM items WHERE id = %s", (item_id,)
        )
        item = cursor.fetchone()
    connection.close()
    return render_template("form.html", item=item)


@app.route("/items/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
    connection.close()
    invalidate_cache()
    return redirect(url_for("list_items"))


# Runs once per worker process, not per request — gunicorn imports this module
# once and forks workers, so the table/connectivity only needs to exist before the first request.
init_db()
wait_for_redis()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
