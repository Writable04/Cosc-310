from fastapi import Depends, HTTPException
from app.routers.dependencies import require_auth, registration, router
from app.schemas.authenticationSchema import AuthenticationResponse

@router.get("/test/auth/{username}/{token}", dependencies=[Depends(require_auth)])
def test_authentication():
    return {"status": "ok" }


@router.post("/register/{username}")
def register(username: str, password: str, validatated_password: str, role: str) -> AuthenticationResponse:
    try:
        token = registration.register(username, password, validatated_password, role)
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