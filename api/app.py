import json
import os
from urllib.parse import unquote_plus

import requests
import validators
from flask import Flask, Response, render_template, render_template_string, request
from hashids import Hashids
from pymongo import MongoClient

app = Flask(__name__)

hash_salt = os.environ.get("HASH_SALT")
hashids = Hashids(salt=hash_salt)

# db setup
db_url = os.environ.get("MONGO_URL")
client = MongoClient(db_url)
db = client["mydb"]
collection = db["links"]


def decode_string(encoded):
    decoded = "".join([chr(i) for i in hashids.decode(encoded)])
    return decoded


def is_valid_url(url):
    return validators.url(url)


def auto_increment_id():
    return int(collection.count_documents({})) + 1


@app.route("/short/v2")
def short_api_v2():
    url = request.args.get("url")
    metadata = request.args.get("meta")
    try:
        org_url = f"{url}&meta={metadata}"
        url_id = auto_increment_id()
        collection.insert_one({"url_id": url_id, "long_url": org_url})
        hashid = hashids.encode(url_id)
        short_url = f"{request.host_url}tg/{hashid}"
        response_data = {
            "org_url": org_url,
            "short_url": short_url,
        }
        json_data = json.dumps(response_data, indent=4)
        return Response(json_data, content_type="application/json")
    except BaseException:
        response_data = {
            "org_url": url,
            "short_url": "https://www.anshumanpm.eu.org",
        }
        json_data = json.dumps(response_data, indent=4)
        return Response(json_data, content_type="application/json")


@app.route("/tg/<id>")
def tg(id):
    try:
        url_id = hashids.decode(id)[0]
        original_url = collection.find_one({"url_id": url_id})["long_url"]
        html = requests.get(original_url).content.decode("utf-8")
        return render_template_string(html)
    except BaseException:
        return render_template("homepage.html", invalid_link=True)


@app.route("/tg/stream")
def tg_stream():
    video_url = request.args.get("url")
    metadata = request.args.get("meta")
    if video_url != "" and metadata != "":
        try:
            data = decode_string(unquote_plus(metadata)).split("|")
            f_name = data[0]
            f_size = data[1]
            f_owner = data[2]
            f_time = data[3]
            return render_template(
                "tg-stream.html",
                video_url=video_url,
                f_name=f_name,
                f_size=f_size,
                f_owner=f_owner,
                f_time=f_time,
            )
        except BaseException:
            return "Invalid Input!"
    return "Invalid URL!"


@app.route("/", methods=["GET", "POST"])
def home_page():
    if request.method == "POST":
        video_url = request.form["url"]
        if is_valid_url(video_url):
            return render_template("stream.html", video_url=video_url)
        else:
            return render_template(
                "homepage.html", input_value=video_url, invalid_link=True
            )
    return render_template("homepage.html")
