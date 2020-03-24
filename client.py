import requests
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# todo now if you write to all we do not encrypt
class EncryptedClient():
    def __init__(self):
        self.username = self.password = None

        while not self.username:
            self.username = input("your username:\t")

        while not self.password:
            self.password = input("your password:\t")

        self.to_whom = input("Whom would you like to write? [All]:\t").lower()

        if not self.to_whom:
            self.to_whom = "all"

        my_private_key_file = f"private_key_{self.username}.pem"
        my_public_key_file = f"public_key_{self.username}.pem"

        friend_private_key_file = f"private_key_{self.to_whom}.pem"
        friend_public_key_file = f"public_key_{self.to_whom}.pem"

        if self.to_whom != "all":
            if os.path.isfile(friend_private_key_file) and os.path.isfile(friend_public_key_file):
                # read keys from files
                with open(friend_private_key_file, "rb") as key_file:
                    self.private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None,
                        backend=default_backend()
                    )
                with open(friend_public_key_file, "rb") as key_file:
                    self.public_key = serialization.load_pem_public_key(
                        key_file.read(),
                        backend=default_backend()
                    )
            else:
                print("Such user does not exist")
                return

        if not os.path.isfile(my_private_key_file) and not os.path.isfile(my_public_key_file):
            # create new keys and write them to the file
            self.my_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.my_public_key = self.my_private_key.public_key()

            # write private key to the file
            pem = self.my_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            with open(my_private_key_file, 'wb') as f:
                f.write(pem)

            # write public key to the file
            pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            with open(my_public_key_file, 'wb') as f:
                f.write(pem)

    def send_message(self, text):
        if self.to_whom.lower() == "all":
            encrypted_text = text
        else:
            encrypted_text = self.encrypt_msg(text)

        message = {"username": self.username,
                   "to_whom": self.to_whom,
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
