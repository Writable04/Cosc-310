from fastapi import APIRouter, Depends, HTTPException

from app import __version__
from app.repositories.storage_accounts import AccountsStorage
from app.services.authentication.auth import Authentication
from app.services.authentication.registration import Registration

router = APIRouter()

storage = AccountsStorage()
authentication = Authentication(storage)
registration = Registration(storage, authentication)


def require_auth(username: str, token: str):
    authentication.authenticate(username, token)
    return True


@router.get("/test/auth/{username}/{token}", dependencies=[Depends(require_auth)])
def test_authentication():
    return {"status": "ok", "version": __version__}


@router.post("/register/{username}")
def register(username: str, password: str, validatated_password: str, role: str):
    try:
        token = registration.register(username, password, validatated_password, role)
        return {"status": "success", "message": "User registered successfully", "token": token}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/login/{username}")
def login(username: str, password: str):
    try:
        token = registration.login(username, password)
        return {"status": "success", "message": "User logged in successfully", "token": token}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))