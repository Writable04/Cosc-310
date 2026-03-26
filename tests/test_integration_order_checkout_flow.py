import json
import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.dependencies import accounts_storage, cart_storage


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def restore_accounts_storage():
    existing = {}
    path = accounts_storage.path
    if path.exists():
        existing = json.loads(path.read_text())

    yield

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2))


@pytest.fixture(autouse=True)
def restore_cart_storage():
    existing = {}
    path = cart_storage.path
    if path.exists():
        existing = json.loads(path.read_text())

    yield

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2))


def test_order_flow_register_through_checkout_ready_cart(client: TestClient) -> None:
    username = uuid.uuid4()
    password = "Password123"
    email = f"{username}@gmail.com"
    role = "admin"

    # register new user
    register_response = client.post(
        f"/authentication/register/{username}",
        params={
            "password": password,
            "validatated_password": password,
            "role": role,
            "email": email,
        },
    )
    assert register_response.status_code == 200
    token = register_response.json()["token"]

    # get restaurant data
    restaurant_response = client.get(f"/dataset/restaurant/1/{username}/{token}")
    assert restaurant_response.status_code == 200
    restaurant_data = restaurant_response.json()
    assert restaurant_data["name"] == "Bobs Burgers"
    menu_id = restaurant_data["restaurant_id"]

    # get menu data for restaurant
    menu_response = client.get(f"/dataset/menu/{menu_id}")
    assert menu_response.status_code == 200
    menu_data = menu_response.json()
    assert menu_data["menu_id"] == menu_id
    assert menu_data["items"]
    assert len(menu_data["menuCombos"]) >= 1

    # get items for menu
    items_by_id = {}
    for item_id in menu_data["items"]:
        item_res = client.get(f"/dataset/item/{item_id}/{username}/{token}")
        assert item_res.status_code == 200
        item = item_res.json()
        assert item["item_id"] == item_id
        assert item["menu_id"] == menu_id
        items_by_id[item_id] = item

    # initialize cart
    init_cart = client.get(f"/cart/{username}/{token}")
    assert init_cart.status_code == 200

    # add items to cart
    for item in items_by_id.values():
        add_res = client.post(
            f"/cart/item/{username}/{token}",
            json={
                "item_id": item["item_id"],
                "name": item["name"],
                "price": str(item["price"]),
                "menu_id": item["menu_id"],
            },
        )
        assert add_res.status_code == 200
        assert add_res.json() is True

    # apply combo to cart
    combo_id = menu_data["menuCombos"][0]["combo_id"]
    combo_response = client.post(
        f"/cart/combo/{username}/{token}",
        params={"combo_id": combo_id, "menu_id": menu_id},
    )
    assert combo_response.status_code == 200

    # get cart to verify items are in cart
    cart_response = client.get(f"/cart/{username}/{token}")
    assert cart_response.status_code == 200
    cart = cart_response.json()

    assert cart["restaurant"] == "Bobs Burgers"
    assert len(cart["appliedCombos"]) > 0
    assert cart["totalDiscount"] == pytest.approx(5.0)
    assert cart["subtotal"] == pytest.approx(185.01)
    assert cart["checkout_total"] == pytest.approx(
        cart["subtotal"] - cart["totalDiscount"]
    )
