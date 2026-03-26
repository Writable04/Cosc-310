from fastapi import APIRouter, Depends, HTTPException
from app.routers.dependencies import cart_storage, require_auth
from app.schemas.cartSchema import Cart
from app.schemas.itemSchema import Item

router = APIRouter()
# i used "theCart" when a cart is returned, and "result" when a boolean is returned

# cart
@router.get("/{username}/{token}", dependencies=[Depends(require_auth)]) 
def get_or_create_cart(username: str) -> Cart:
    theCart = cart_storage.loadUserCart(username)
    if not theCart:
        raise HTTPException(status_code=400, detail="Cart could not be retrieved")
    return theCart

@router.put("/{username}/{token}", dependencies=[Depends(require_auth)])
def clear_cart_contents(username: str) -> Cart:
    result = cart_storage.clearUserCart(username)
    if not result:
        raise HTTPException(status_code=400, detail="Cart could not be cleared")
    return result

@router.delete("/{username}/{token}", dependencies=[Depends(require_auth)])
def remove_cart_from_db(username: str):
    result = cart_storage.removeCart(username)
    if not result:
        raise HTTPException(status_code=400, detail="Cart could not be removed")
    return result

# cart items
@router.post("/item/{username}/{item_id}/{token}", dependencies=[Depends(require_auth)])
def add_item(username: str, item_id: int):
    result = cart_storage.addItem(username, item_id)
    if not result:
        raise HTTPException(status_code=400, detail="Item could not be added")
    return result

@router.delete("/item/{username}/{item_id}/{token}", dependencies=[Depends(require_auth)])
def remove_item(username: str, item_id: int):
    result = cart_storage.removeItem(username, item_id)
    if not result:
        raise HTTPException(status_code=400, detail="Item could not be removed")
    return result

# combos
@router.post("/combo/{username}/{combo_id}/{token}", dependencies=[Depends(require_auth)], response_model=Cart)
def add_combo(username: str, combo_id: int) -> Cart:
    result = cart_storage.addCombo(username, combo_id)
    if not result:
        raise HTTPException(status_code=400, detail="Combo could not be applied")
    return result

@router.delete("/combo/{username}/{combo_id}/{token}", dependencies=[Depends(require_auth)])
def remove_combo(username: str, combo_id: int):
    result = cart_storage.removeCombo(username, combo_id)
    if not result:
        raise HTTPException(status_code=400, detail="Combo could not be removed")
    return result