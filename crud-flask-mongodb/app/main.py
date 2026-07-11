import os
import time

from bson import ObjectId
from flask import Flask, redirect, render_template, request, url_for
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = Flask(__name__)

# A single MongoClient is created once and reused across requests — pymongo
# already pools connections internally, unlike psycopg2 in the PostgreSQL
# Template, which opens/closes a connection per request.
client = MongoClient(
    host=os.environ["MONGO_HOST"],
    port=int(os.environ["MONGO_PORT"]),
    username=os.environ["MONGO_USERNAME"],
    password=os.environ["MONGO_PASSWORD"],
    authSource="admin",
)
items = client[os.environ["MONGO_DB"]]["items"]


def wait_for_mongo():
    # MongoDB may still be starting when this container boots — retry instead of crashing.
    for _ in range(10):
        try:
            client.admin.command("ping")
            return
        except ConnectionFailure:
            time.sleep(2)

    raise RuntimeError("Could not connect to MongoDB after 10 attempts")


@app.route("/")
def list_items():
    return render_template("index.html", items=items.find().sort("_id"))


@app.route("/items/new", methods=["GET", "POST"])
def create_item():
    if request.method == "POST":
        items.insert_one(
            {"name": request.form["name"], "description": request.form["description"]}
        )
        return redirect(url_for("list_items"))
    return render_template("form.html", item=None)


@app.route("/items/<item_id>/edit", methods=["GET", "POST"])
def edit_item(item_id):
    if request.method == "POST":
        items.update_one(
            {"_id": ObjectId(item_id)},
            {
                "$set": {
                    "name": request.form["name"],
                    "description": request.form["description"],
                }
            },
        )
        return redirect(url_for("list_items"))

    item = items.find_one({"_id": ObjectId(item_id)})
    return render_template("form.html", item=item)


@app.route("/items/<item_id>/delete", methods=["POST"])
def delete_item(item_id):
    items.delete_one({"_id": ObjectId(item_id)})
    return redirect(url_for("list_items"))


# Runs once per worker process, not per request — gunicorn imports this module
# once and forks workers, so connectivity only needs to be confirmed before the first request.
wait_for_mongo()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
