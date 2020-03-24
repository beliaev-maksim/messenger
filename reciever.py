from datetime import datetime
import requests
import time


after = 0


def get_message(after):
    response = requests.get("http://127.0.0.1:5000/messages",
                            params={"after": after})
    data = response.json()
    return data["messages"]


def print_message(messages):

    for message in messages:
        time_mes = datetime.fromtimestamp(message["time"]).strftime("%D %H:%M")
        print(time_mes, ":\t", message["username"], ":\t", message["text"])


while True:
    messages = get_message(after)

    if messages:
        after = messages[-1]["time"]
        print_message(messages)

    time.sleep(5)




