import os
from dotenv import load_dotenv
from jwcrypto import jwk

def __get_jwks():
    load_dotenv(dotenv_path="dev.env")
    kid = os.getenv('KID')

    with open('certs/public.pem', 'rb') as f:
        pem_data = f.read()

    print(pem_data)
    key = jwk.JWK.from_pem(pem_data)
    key.update({
        "kid": kid,
        "use": 'sig',
        "alg": 'RS256'
    })

    jwks = jwk.JWKSet()
    jwks.add(key)

    jwksJson = jwks.export(private_keys=False, as_dict=True)

    print(jwksJson)

    return jwksJson