from app.repositories.storage_accounts import AccountsStorage
from app.services.authentication.auth import Authentication

storage = AccountsStorage()
authentication = Authentication(storage)


def require_auth(username: str, token: str) -> bool:
    authentication.authenticate(username, token)
    return True
