from fastapi import APIRouter, HTTPException
from app.repositories.storage_accounts import AccountsStorage
from app.services.notifications.notifications import Notification

router = APIRouter()

storage = AccountsStorage()
notifications_server = Notification()

@router.post("/send/{username}/{token}")
def send_notification(customer_username: str, subject: str, msg: str):
    email = storage.get_account_email(customer_username)
    if (email is not None):
        try:
            notifications_server.send_notification(subject, msg, email)
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error))