# import pytest
# import json
# from pathlib import Path
# from app.schemas.cartSchema import Cart, CartItem
# from app.repositories.storage_base import Storage
# from app.repositories.cart_repo import CartStorage
# from app.repositories.item_repo import ItemStorage
# from app.repositories.menu_repo import MenuStorage

# @pytest.fixture
# def storage(tmp_path):
#     test_file = tmp_path / "cart.json"
#     storage = CartStorage(path=test_file)
#     return storage

# @pytest.fixture
# def exampleCart():
#     return Cart.model_construct(user_id=123, restaurant="Tomi's House", items=[{
#         "name": "Sushi",
#         "itemID": 4,
#         "quantity": 1,
#         "price": 8.53
#       }], subtotal=8.53)

# def test_loadUserCart(UserID):
#     CartStorage().loadUserCart(123)
#     CartStorage().removeCart(123)

#     result = CartStorage().loadUserCart(UserID)
#     assert result == Cart(user_id=UserID, restaurant="", items=[], subtotal=0.00)

# def test_clearUserCart(UserID):
#     CartStorage().loadUserCart(123)
#     CartStorage().clearUserCart(123)
#     CartStorage().addItem(123, 4)
    
#     result = CartStorage().clearUserCart(UserID)
#     assert result == Cart(user_id=UserID, restaurant="", items=[], subtotal=0.00)

# def test_removeCart(UserID):
#     CartStorage().loadUserCart(123)
#     result = CartStorage().removeCart(UserID)
#     with open('cart.json', 'r') as file:
#         data = json.load(file)
        
#     assert data[str(UserID)] == None

# def test_addItem(UserID, ItemID):
#     result = CartStorage().addItem(UserID, ItemID)
#     assert result == True

# def test_removeItem(UserID, ItemID):
#     result = CartStorage().removeItem(UserID, ItemID)
#     assert result == True