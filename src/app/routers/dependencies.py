from app.repositories.storage_accounts import AccountsStorage
from app.services.authentication.auth import Authentication
from app.services.authentication.registration import Registration

storage = AccountsStorage()
authentication = Authentication(storage)
registration = Registration(storage, authentication)


def require_auth(username: str, token: str) -> bool:
    authentication.authenticate(username, token)
    return True
