
from typing import Dict
from fastapi import Depends, FastAPI

from call_pkj_api import __create_jwt
from jwks import __get_jwks
from oauth_util import __validate_token
from rotate import __create_secrets

app = FastAPI()

@app.get("/")
def read_root():
    return {"Welcome...."}

@app.get("/rotate")
def rotate():
    __create_secrets()
    return "New Certificates created..."

@app.get("/client")
def client():
    return __create_jwt()

@app.get("/jwks")
def jwks():
    return __get_jwks()

@app.get("/protected_api")
def api_response(claims: Dict = Depends(__validate_token)):
    print("Decoded JWT claims:", claims)

    return {
        "message": "Token is valid.  Here is your response.",
        "claims": claims
    }

