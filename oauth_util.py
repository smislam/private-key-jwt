import requests
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict

KEYCLOAK_BASE_URL = 'http://localhost:8080/realms/master/'
OPENID_CONFIG_URL = f'{KEYCLOAK_BASE_URL}/.well-known/openid-configuration'

oidc_config = requests.get(OPENID_CONFIG_URL).json()
JWKS_URI    = oidc_config['jwks_uri']
ISSUER      = oidc_config['issuer']
TOKEN_URL   = oidc_config['token_endpoint']
audience    = 'account' # Keycloak sets the audience as 'account'.

JWKS = requests.get(JWKS_URI).json()
bearer_scheme = HTTPBearer(bearerFormat="JWT")

def __get_matched_jwk(token: str) -> Dict:
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    # Find the matching JWK
    for jwk in JWKS["keys"]:
        if jwk["kid"] == kid:
            return jwk

async def __validate_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict:
    token = credentials.credentials

    jwk = __get_matched_jwk(token)

    try:
        valid_jwt = jwt.decode(
            token,
            jwk,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=audience
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token validation failed: {e}"
        )


    return valid_jwt