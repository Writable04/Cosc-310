from fastapi import APIRouter
from app.repositories.cart_repo import CartStorage
from app.schemas.cartSchema import Cart, CartItem

router = APIRouter()
cs = CartStorage()

# cart
@router.get("/cart") 
def get_or_create_cart(UserID: int) -> Cart:
    return cs.loadUserCart(UserID)

@router.put("/cart")
def clear_cart_contents(UserID: int) -> Cart:
    return cs.clearUserCart(UserID)

@router.delete("/cart")
def remove_cart_from_db(UserID: int):
    return cs.removeCart(UserID)

# cart items
@router.post("/cartItem")
def add_item(UserID: int, ItemID: int):
    return cs.addItem(UserID, ItemID)

@router.delete("/cartItem")
def remove_item(UserID: int, ItemID: int):
    return cs.removeItem(UserID, ItemID)

@router.get("/Subtotal")
def getSubtotal(user_id:str):
    return cs.readSubtotal(user_id)

@router.get("/ComboDiscount")
def getDiscount():
    return getComboDiscount()