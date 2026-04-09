from fastapi import APIRouter, HTTPException
from app.routers.dependencies import accounts_storage, reset_password
router = APIRouter()

@router.post("/{username}/{new_password}/{validated_password}/{one_time_code}")
def reset_pass(username: str, new_password: str, validated_password: str, one_time_code: int):
    data = accounts_storage.get_account_info(username)
    if data is None:
        raise HTTPException(status_code=404, detail="Account not found")
    try:
        reset_password.reset_password(username, new_password, validated_password, one_time_code)
        return "Password successfully reset."
    except HTTPException as error: 
        HTTPException(status_code=400, detail=str(error))

@router.post("/{username}")
def send_one_time_code(username: str):
    try:
        reset_password.send_one_time_code(username)
        return "Code sent."
    except HTTPException as error:
        HTTPException(status_code=400, detail=str(error))