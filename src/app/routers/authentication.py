from fastapi import APIRouter, Depends, HTTPException
from app.routers.dependencies import accounts_storage, require_auth, registration
from app.schemas.authenticationSchema import AccountInfo, AuthenticationResponse
from app.repositories.reset_password_repo import ResetPassword
router = APIRouter()

@router.post("/register/{username}")
def register(username: str, password: str, validatated_password: str, role: str, email: str, address: str = "") -> AuthenticationResponse:
    try:
        token = registration.register(username, password, validatated_password, role, email, address=address)
        return {"status": "success", "message": "User registered successfully", "token": token}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.post("/login/{username}")
def login(username: str, password: str) -> AuthenticationResponse:
    try:
        token = registration.login(username, password)
        return {"status": "success", "message": "User logged in successfully", "token": token}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@router.get("/account/{username}/{token}" , dependencies=[Depends(require_auth)])
def get_account_info(username: str) -> dict:
    account = accounts_storage.get_account_info(username)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"email": account.email, "role": account.role, "address": account.address, "locked": account.locked, "consecutive login fails": account.consecutive_password_fails}