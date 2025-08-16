import os
import time
import uuid
from dotenv import load_dotenv
import requests
from jwcrypto import jwk, jwt

def __create_jwt():

    load_dotenv(dotenv_path="dev.env")
    password = os.getenv('PKEY_PASSWORD')
    kid = os.getenv('KID')

    with open('certs/private.pem', 'rb') as f:
        pem_data = f.read()

    key = jwk.JWK.from_pem(pem_data, password=password.encode('utf-8'))
    key.update({
        "kid": kid,
        "use": 'sig',
        "alg": 'RS256'
    })

    now = int(time.time())
    client_id = 'client-42'
    token_url = 'http://localhost:8080/realms/master/protocol/openid-connect/token'

    header = {
        'alg': 'RS256',
        'typ': 'JWT',
        'kid': key.get('kid')
    }

    claims = {
        'iss': client_id,
        'sub': client_id,
        'aud': token_url,
        'iat': now,
        'exp': now + 300,
        'jti': str(uuid.uuid4())
    }

    token = jwt.JWT(header=header, claims=claims)
    token.make_signed_token(key) 

    client_assertion = token.serialize()

    data = {
        'grant_type': 'client_credentials',
        'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
        'client_assertion': client_assertion,
        # 'scope': 'xxx' //Add any custom scopes here
    }

    resp = requests.post(token_url, data=data)
    
    # Create Bearer request
    headers = {"Authorization": f"Bearer {resp.json().get('access_token')}"}    
    apiResponse = requests.get('http://localhost:8000/protected_api', headers=headers)
    apiResponse.raise_for_status()
    return apiResponse.json()
