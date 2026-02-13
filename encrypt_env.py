import os
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass

def get_key(password):
    salt = b'salt_' # In a real app, this should be random and stored/shared, but for simple sharing we can fix it or store it in the file header.
    # For simplicity in this script, we'll use a fixed salt so the password is the only thing needed.
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_file(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    password = getpass.getpass("Enter encryption password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("Passwords do not match.")
        return

    key = get_key(password)
    f = Fernet(key)
    
    with open(file_path, "rb") as file:
        file_data = file.read()
        
    encrypted_data = f.encrypt(file_data)
    
    output_path = file_path + ".enc"
    with open(output_path, "wb") as file:
        file.write(encrypted_data)
        
    print(f"File encrypted to {output_path}")

if __name__ == "__main__":
    encrypt_file(".env")
