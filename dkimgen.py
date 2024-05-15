import requests
from requests.auth import HTTPBasicAuth
import random
import string
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_dkim_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_key_pem.decode('utf-8'), public_key_pem.decode('utf-8')