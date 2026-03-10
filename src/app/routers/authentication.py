from fastapi import APIRouter, HTTPException
from app.repositories.storage_accounts import AccountsStorage
from app.services.authentication.auth import Authentication
from app.services.authentication.registration import Registration

router = APIRouter()

storage = AccountsStorage()
authentication = Authentication(storage)
registration = Registration(storage, authentication)


@router.post("/register/{username}") 
def register(username: str, password: str, validatated_password: str, role: str):
    try:
        registration.register(username, password, validatated_password, role)
        return {"status": "success", "message": "User registered successfully"}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))