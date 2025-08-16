import os
import uuid
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv, set_key
from jwcrypto import jwk

def __create_secrets():
    load_dotenv()    
    kid = str(uuid.uuid4())
    key_password = str(uuid.uuid4())
    set_key('dev.env', 'KID', kid)
    set_key('dev.env', 'PKEY_PASSWORD', key_password)

    key = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, key_size=4096)
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM, 
        format=serialization.PrivateFormat.PKCS8, 
        encryption_algorithm=serialization.BestAvailableEncryption(key_password.encode('utf-8'))
    )
        
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo) 

    private_key_str = private_pem.decode('utf-8')
    public_key_str = public_key.decode('utf-8')

    put_secret(private_key_str, "private.pem")
    put_secret(public_key_str, "public.pem")    

def put_secret(payload: str, filename: str):
    with open ("certs/" + filename, "w") as cert_file:
        cert_file.write(payload)