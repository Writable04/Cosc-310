from fastapi import Depends, HTTPException
from app.routers.dependencies import router, storage, notifications_server, require_auth


@router.post("/send/{username}/{token}", dependencies=[Depends(require_auth)])
def send_notification(customer_username: str, subject: str, msg: str):
    email = storage.get_account_email(customer_username)
    if (email is not None):
        try:
            notifications_server.send_notification(subject, msg, email)
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error))