import pytest
import json
from pathlib import Path
from app.schemas.cartSchema import Cart, CartItem
from app.repositories.storage_base import Storage
from app.repositories.cart_repo import CartStorage
from app.repositories.item_repo import ItemStorage
from app.repositories.menu_repo import MenuStorage

@pytest.fixture
def storage(tmp_path):
    test_file = tmp_path / "cart.json"
    storage = CartStorage(path=test_file)
    return storage

def test_loadNewUserCart() -> Cart:
    userID = "123"
    CartStorage().loadUserCart(userID) # make sure theres no preexisting entry
    CartStorage().removeCart(userID)   # make sure theres no preexisting entry

    result = CartStorage().loadUserCart(userID)
    emptyCart = Cart(
                user_id=userID,
                restaurant="",
                items=[],
                subtotal=0.00,
                appliedCombos=[],
                totalDiscount=0.00,
                checkout_total=0.00
            )
    assert result == emptyCart

def test_clearUserCart() -> bool:
    userID = "123"
    CartStorage().loadUserCart(userID)  
    CartStorage().clearUserCart(userID) 
    CartStorage().addItem(userID, 4)
    
    result = CartStorage().clearUserCart(userID)
    assert result == True
    emptyCart = Cart(
                user_id=userID,
                restaurant="",
                items=[],
                subtotal=0.00,
                appliedCombos=[],
                totalDiscount=0.00,
                checkout_total=0.00
            )
    assert CartStorage().loadUserCart(userID) == emptyCart

def test_removeCart():
    userID = "123"
    CartStorage().loadUserCart(userID)
    CartStorage().clearUserCart(userID) 
    result = CartStorage().removeCart(userID)
    assert result == True

def test_addItem():
    userID = "123"
    itemID = 4
    exampleCart = Cart(user_id="123", 
                                restaurant="Pops Pizza", 
                                items=[{
        "name": "Sushi",
        "itemID": 4,
        "quantity": 1,
        "price": 8.53
      }], subtotal=8.53,
      appliedCombos=[],
      totalDiscount=0.00,
      checkout_total=8.53
    )
    CartStorage().loadUserCart(userID)  
    CartStorage().clearUserCart(userID) 
    result = CartStorage().addItem(userID, itemID)
    assert result == True
    assert CartStorage().loadUserCart(userID) == exampleCart

def test_removeItem():
    userID = "123"
    itemID = 4
    CartStorage().loadUserCart(userID)  
    CartStorage().clearUserCart(userID) 
    CartStorage().addItem(userID, itemID)

    result = CartStorage().removeItem(userID, itemID)
    assert result == True
    emptyCart = Cart(
                user_id=userID,
                restaurant="",
                items=[],
                subtotal=0.00,
                appliedCombos=[],
                totalDiscount=0.00,
                checkout_total=0.00
            )
    assert CartStorage().loadUserCart(userID) == emptyCart

# ADD COMBO TESTS