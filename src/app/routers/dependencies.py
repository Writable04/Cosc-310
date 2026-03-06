from app.repositories.storage_accounts import AccountsStorage
from app.services.authentication.auth import Authentication
from app.services.authentication.registration import Registration
from fastapi import APIRouter, HTTPException, Request

router = APIRouter()

storage = AccountsStorage()
authentication = Authentication(storage)
registration = Registration(storage, authentication)

admin_routes=['test/auth']

def require_auth(username: str, token: str, request: Request) -> bool:
    authentication.authenticate(username, token)
    for admin_route in admin_routes:
        route = request.scope.get("route").path
        if admin_route in route and storage.get_account_role(username) != 'admin':
            raise HTTPException(status_code=401, detail="Unauthorized")
        
    return True
