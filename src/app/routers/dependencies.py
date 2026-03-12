from app.repositories.storage_accounts import AccountsStorage
from app.services.authentication.auth import Authentication
from app.services.authentication.registration import Registration
from fastapi import HTTPException, Request
from app.services.notifications.notifications import Notification

storage = AccountsStorage()
authentication = Authentication(storage)
registration = Registration(storage, authentication)
notifications_server = Notification()

admin_routes=['test/auth']

def require_auth(username: str, token: str, request: Request) -> bool:
    authentication.authenticate(username, token)
    for admin_route in admin_routes:
        route = request.scope.get("route").path
        if admin_route in route and storage.get_account_role(username) != 'admin':
            raise HTTPException(status_code=401, detail="Unauthorized")
        
    return True
