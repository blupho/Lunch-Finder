import os
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass

def get_key(password):
    salt = b'salt_' 
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def decrypt_file(file_path):
    enc_path = file_path + ".enc"
    if not os.path.exists(enc_path):
        print(f"File {enc_path} not found.")
        return

    password = getpass.getpass("Enter decryption password: ")
    key = get_key(password)
    f = Fernet(key)
    
    try:
        with open(enc_path, "rb") as file:
            encrypted_data = file.read()
            
        decrypted_data = f.decrypt(encrypted_data)
        
        with open(file_path, "wb") as file:
            file.write(decrypted_data)
            
        print(f"File decrypted to {file_path}")
    except Exception as e:
        print("Decryption failed. Wrong password?")

if __name__ == "__main__":
    decrypt_file(".env")
