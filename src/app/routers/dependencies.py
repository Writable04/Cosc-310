from app.repositories.item_repo import ItemStorage
from app.repositories.menu_repo import MenuStorage
from app.repositories.resturant_repo import ResturantStorage
from app.repositories.storage_accounts import AccountsStorage
from app.services.authentication.auth import Authentication
from app.services.authentication.registration import Registration
from fastapi import HTTPException, Request
from app.services.notifications.notifications import Notification
from app.repositories.cart_repo import CartStorage


accounts_storage = AccountsStorage()
authentication = Authentication(accounts_storage)
registration = Registration(accounts_storage, authentication)
notifications_server = Notification()
resturant_storage = ResturantStorage()
menu_storage = MenuStorage()
item_storage = ItemStorage()
cart_storage = CartStorage()

admin_routes=['/notification']
resturant_manager_routes=['/dataset']

def require_auth(username: str, token: str, request: Request) -> bool:
    authentication.authenticate(username, token)
    route = request.scope.get("route").path
    method = request.method.upper()
    role = accounts_storage.get_account_role(username)
    if (role == 'admin'):
        return True
    
    for admin_route in admin_routes:
        if route.startswith(admin_route):
            raise HTTPException(status_code=401, detail="Unauthorized")

    for resturant_manager_route in resturant_manager_routes:
        if role != 'manager' and route.startswith(resturant_manager_route) and method in {"POST", "PUT", "DELETE"}:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
    return True

def require_resturant_manager(username: str, id: int | None) -> bool:
    if id is None:
        raise HTTPException(status_code=404, detail="Not Found")

    resturant = resturant_storage.find_resturant(id)
    user_role = accounts_storage.get_account_role(username)
    if user_role is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    elif (username != resturant.owner and user_role != 'admin'):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return True