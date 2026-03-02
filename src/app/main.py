from fastapi import FastAPI, HTTPException

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


@app.get("/")
def root() -> HealthResponse:
    return {"status": "ok", "version": __version__}


@app.post("/register/{username}")
def register(username: str, password: str, validatated_password: str, role: str):
    try:
        registration.register(username, password, validatated_password, role)
        return {"status": "success", "message": "User registered successfully"}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/login/{username}")
def login(username: str, password: str):
    try:
        registration.login(username, password)
        return {"status": "success", "message": "User logged in successfully"}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))