from fastapi import APIRouter, Depends
from app.routers.dependencies import cart_storage, require_auth
from app.schemas.cartSchema import Cart
from app.schemas.itemSchema import Item

router = APIRouter()

# cart
@router.get("/{username}/{token}", dependencies=[Depends(require_auth)]) 
def get_or_create_cart(username: str) -> Cart:
    return cart_storage.loadUserCart(username)

@router.put("/{username}/{token}", dependencies=[Depends(require_auth)])
def clear_cart_contents(username: str) -> Cart:
    return cart_storage.clearUserCart(username)

@router.delete("/{username}/{token}", dependencies=[Depends(require_auth)])
def remove_cart_from_db(username: str):
    return cart_storage.removeCart(username)

# cart items
@router.post("/item/{username}/{token}", dependencies=[Depends(require_auth)])
def add_item(username: str, item: Item):
    return cart_storage.addItem(username, item.item_id)

@router.delete("/item/{username}/{token}", dependencies=[Depends(require_auth)])
def remove_item(username: str, item: Item):
    return cart_storage.removeItem(username, item.item_id)
