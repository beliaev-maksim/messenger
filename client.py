import requests
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


class EncryptedClient():
    def __init__(self):
        self.username = input("your username:\t")
        self.password = input("your password:\t")

        if os.path.isfile('private_key.pem') and os.path.isfile('public_key.pem'):
            # read keys from files
            with open("private_key.pem", "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
            with open("public_key.pem", "rb") as key_file:
                self.public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )

        else:
            # create new keys and write them to the file
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()

            # write private key to the file
            pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            with open('private_key.pem', 'wb') as f:
                f.write(pem)

            # write public key to the file
            pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            with open('public_key.pem', 'wb') as f:
                f.write(pem)

    def send_message(self, text):
        encrypted_text = self.encrypt_msg(text)
        message = {"username": self.username,
                   "password": self.password,
                   "text": encrypted_text}
        response = requests.post("http://127.0.0.1:5000/send", json=message)

        return response.status_code == 200

    def encrypt_msg(self, text):
        encrypted = self.public_key.encrypt(
            text.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        b64_string = str(base64.b64encode(encrypted), 'utf-8')
        return b64_string

    def run(self):
        while True:
            text = input("Your message:\t")
            result = self.send_message(text)

            if not result:
                print("Error")


if __name__ == "__main__":
    my_client = EncryptedClient()
    my_client.run()
