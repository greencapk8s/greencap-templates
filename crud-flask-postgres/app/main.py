import os
import time

import psycopg2
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


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


@app.route("/")
def list_items():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, description FROM items ORDER BY id")
        items = cursor.fetchall()
    connection.close()
    return render_template("index.html", items=items)


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
    return redirect(url_for("list_items"))


# Runs once per worker process, not per request — gunicorn imports this module
# once and forks workers, so the table only needs to exist before the first request.
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
