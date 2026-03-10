from app.repositories.storage_accounts import AccountsStorage
from app.services.authentication.auth import Authentication
from app.services.authentication.registration import Registration
from app.services.notifications.notifications import Notification

storage = AccountsStorage()
authentication = Authentication(storage)
registration = Registration(storage, authentication)
notifications_server = Notification()

def require_auth(username: str, token: str) -> bool:
    authentication.authenticate(username, token)
    return True
