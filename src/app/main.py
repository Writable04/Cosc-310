from fastapi import FastAPI, HTTPException, Depends

from app import __version__
from app.authentication.auth import Authentication
from app.authentication.registration import Registration
from app.db.storage_accounts import AccountsStorage
from app.models import HealthResponse

app = FastAPI(
    title="COSC 310 Project",
    version=__version__,
)


storage = AccountsStorage()
authentication = Authentication(storage)
registration = Registration(storage, authentication)


@app.get("/test/auth/{username}/{token}", dependencies=[Depends(authentication.authenticate)])
def test_authentication() -> HealthResponse:
    return {"status": "ok", "version": __version__}


@app.get("/")
def root() -> HealthResponse:
    return {"status": "ok", "version": __version__}


@app.post("/register/{username}")
def register(username: str, password: str, validatated_password: str, role: str):
    try:
        token =registration.register(username, password, validatated_password, role)
        return {"status": "success", "message": "User registered successfully", "token": token}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/login/{username}")
def login(username: str, password: str):
    try:
        token = registration.login(username, password)
        return {"status": "success", "message": "User logged in successfully", "token": token}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))