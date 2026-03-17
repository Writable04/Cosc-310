from app.repositories.item_repo import ItemStorage
from app.repositories.menu_repo import MenuStorage
from app.repositories.resturant_repo import ResturantStorage
from app.repositories.storage_accounts import AccountsStorage
from app.services.authentication.auth import Authentication
from app.services.authentication.registration import Registration
from fastapi import HTTPException, Request
from app.services.notifications.notifications import Notification


accounts_storage = AccountsStorage()
authentication = Authentication(accounts_storage)
registration = Registration(accounts_storage, authentication)
notifications_server = Notification()
resturant_storage = ResturantStorage()
menu_storage = MenuStorage()
item_storage = ItemStorage()

admin_routes=['test/auth', 'notification']
resturant_manager_routes=[]

def require_auth(username: str, token: str, request: Request) -> bool:
    authentication.authenticate(username, token)
    route = request.scope.get("route").path
    role = accounts_storage.get_account_role(username)
    if (role == 'admin'):
        return True

    for admin_route in admin_routes:
        if admin_route in route:
            raise HTTPException(status_code=401, detail="Unauthorized")

    for resturant_manager_route in resturant_manager_routes:
        if resturant_manager_route in route and role != 'manager':
            raise HTTPException(status_code=401, detail="Unauthorized")
        
    return True
