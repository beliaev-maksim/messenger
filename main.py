from flask import Flask, request, abort
from datetime import datetime
import time

app = Flask(__name__)
messages = []

users = {
    "Maksim": "123"
}

@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/status")
def status():
    data = {
        "status": True,
        "name": "ChikChikMessage",
        "time": datetime.now()
    }
    return data


@app.route("/send", methods=["POST"])
def send():
    username = request.json["username"]
    password = request.json["password"]

    if username in users:
        if password != users[username]:
            return abort(401)

    else:
        users[username] = password

    text = request.json["text"]
    current_time = time.time()

    message = {
        "username": username,
        "text": text,
        "time": current_time
    }
    messages.append(message)

    data = {
        "ok": True
    }
    return data


@app.route("/messages")
def all_messages():
    time_mes = float(request.args.get("after"))
    filtered_messages = [message for message in messages if message["time"] > time_mes]
    return {"messages": filtered_messages}

app.run()