from datetime import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import requests
import time
import base64
import os


after = 0
username = None

while not username:
    username = input("your username:\t")

private_key_file = f"private_key_{username}.pem"
if os.path.isfile(private_key_file):
    # read keys from files
    with open(private_key_file, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
else:
    print("Such user does not exist. Run client.py for that user first")


def get_message(after):
    response = requests.get("http://127.0.0.1:5000/messages",
                            params={"after": after})
    data = response.json()
    return data["messages"]


def decrypt_msg(encrypted):
    encrypted = base64.b64decode(encrypted)
    # todo so far assume that key exists
    original_message = private_key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return original_message


def print_message(messages):

    for message in messages:
        if message["to_whom"].lower() not in ["all", username.lower()]:
            continue

        time_mes = datetime.fromtimestamp(message["time"]).strftime("%D %H:%M")
        try:
            if message["to_whom"].lower() == "all":
                message_text = message["text"]
            else:
                message_text = decrypt_msg(message["text"])

            print(time_mes, ":\t", message["username"], ":\t", message_text)
        except ValueError:
            print("Key was changed, message cannot be shown")


while True:
    messages = get_message(after)

    if messages:
        after = messages[-1]["time"]
        print_message(messages)

    time.sleep(5)




