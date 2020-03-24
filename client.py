import requests


def send_message(username, password, text):
    message = {"username": username,
               "password": password,
               "text": text}
    response = requests.post("http://127.0.0.1:5000/send", json=message)

    return response.status_code == 200


username = input("your username:\t")
password = input("your password:\t")
while True:
    text = input("Your message:\t")
    result = send_message(username, password, text)

    if not result:
        print("Error")


