import pytest
from app.repositories.cart_repo import CartStorage


@pytest.fixture
def storage(tmp_path):
    return CartStorage(path=tmp_path / "cart.json")


def test_addCombo(storage):
    user_id = "bob"

    storage.loadUserCart(user_id)

    result = storage.addCombo(user_id, combo_id=1, menu_id=1)

    assert result is True

    cart = storage.read(user_id)

    assert cart is not None
    assert cart["restaurant"] == "Bobs Burgers"
    assert cart["subtotal"] == 65.77
    assert cart["totalDiscount"] == 5.0
    assert cart["checkout_total"] == 60.77

    assert cart["items"] == [
        {"name": "Burritos", "itemID": 1, "quantity": 1, "price": 25.68},
        {"name": "Pizza", "itemID": 13, "quantity": 1, "price": 40.09},
    ]
    assert cart["appliedCombos"] == [
        {
            "combo_id": 1,
            "comboItems": [1, 13],
            "discountPrice": 5.0,
            "quantity": 1,
        }
    ]


def test_removeCombo(storage):
    user_id = "bob"

    storage.loadUserCart(user_id)
    storage.addCombo(user_id, combo_id=1, menu_id=1)

    result = storage.removeCombo(user_id, combo_id=1)

    assert result is True

    cart = storage.read(user_id)

    assert cart is not None
    assert cart["restaurant"] == ""
    assert cart["items"] == []
    assert cart["appliedCombos"] == []
    assert cart["subtotal"] == 0.0
    assert cart["totalDiscount"] == 0
    assert cart["checkout_total"] == 0.0
