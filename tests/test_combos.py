def test_get_combo_discount():
    cart = {
        "items": [
            {"itemID": 101, "price": 10.0, "quantity": 1},
            {"itemID": 102, "price": 5.0, "quantity": 1}
        ]
    }

    class MockMenu:
        def __init__(self):
            self.menuCombos = [
                {"comboItems": [101, 102], "discountRate": 0.2}
            ]

    class TestStorage(CartStorage):
        def find_menu(self, menu_id):
            return MockMenu()

    storage = TestStorage()

    result = storage.getComboDiscount(1, cart)

    assert result == 12.0