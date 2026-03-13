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
cart = CartStorage()

admin_routes=['test/auth', 'notification']

def require_auth(username: str, token: str, request: Request) -> bool:
    authentication.authenticate(username, token)
    for admin_route in admin_routes:
        route = request.scope.get("route").path
        if admin_route in route and accounts_storage.get_account_role(username) != 'admin':
            raise HTTPException(status_code=401, detail="Unauthorized")
        
    return True