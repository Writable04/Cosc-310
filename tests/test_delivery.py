import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.deliverySchema import DeliveryStatus, DeliveryOrder
from app.services.delivery.delivery import DeliveryService

client = TestClient(app)

def _make_order(order_id="order-1", status=DeliveryStatus.PENDING, restaurant="Pizza Palace"):
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    return DeliveryOrder(
        order_id=order_id, username="testuser", restaurant=restaurant,
        items=[], total=49.99, status=status,
        created_at=now.isoformat(), updated_at=now.isoformat(),
        estimated_delivery=(now + timedelta(seconds=45)).isoformat(),
    )

def _mock_maps(MockAcct, MockRest, MockMap):
    MockAcct.return_value.get_address.return_value = "975 Academy Way, Kelowna, BC"
    MockRest.return_value.find_resturant_query.return_value = MagicMock(restaurantAddress="120 Old Vernon Rd, Kelowna, BC")
    MockMap.return_value.calculateDeliveryTimeMins.return_value = 12


def test_start_delivery_creates_order():
    with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo, \
         patch("app.services.delivery.delivery.AccountsStorage") as MockAcct, \
         patch("app.services.delivery.delivery.ResturantStorage") as MockRest, \
         patch("app.services.delivery.delivery.MapStorage") as MockMap, \
         patch("app.services.delivery.delivery.Notification"):
        _mock_maps(MockAcct, MockRest, MockMap)
        MockAcct.return_value.get_account_info.return_value = MagicMock(email="t@t.com", username="testuser")
        MockRepo.return_value.save_order.side_effect = lambda o: o
        order = DeliveryService().start_delivery("testuser", "Pizza Palace", [], 49.99)
    assert order.status == DeliveryStatus.PENDING
    assert order.restaurant == "Pizza Palace"


def test_get_order_returns_with_eta():
    with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo, \
         patch("app.services.delivery.delivery.AccountsStorage"):
        MockRepo.return_value.get_order.return_value = _make_order(status=DeliveryStatus.IN_TRANSIT)
        resp = DeliveryService().get_order("order-1")
    assert resp.status == DeliveryStatus.IN_TRANSIT
    assert isinstance(resp.eta_seconds, int)


def test_eta_is_none_when_delivered():
    with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo, \
         patch("app.services.delivery.delivery.AccountsStorage"):
        MockRepo.return_value.get_order.return_value = _make_order(status=DeliveryStatus.DELIVERED)
        resp = DeliveryService().get_order("order-1")
    assert resp.eta_seconds is None


def test_update_status():
    updated = _make_order(status=DeliveryStatus.IN_PROCESS)
    with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo, \
         patch("app.services.delivery.delivery.AccountsStorage") as MockAcct, \
         patch("app.services.delivery.delivery.Notification"):
        MockAcct.return_value.get_account_info.return_value = MagicMock(email="t@t.com", username="testuser")
        MockRepo.return_value.update_status.return_value = updated
        resp = DeliveryService().update_status("order-1", DeliveryStatus.IN_PROCESS)
    assert resp.status == DeliveryStatus.IN_PROCESS


def test_get_past_orders():
    orders = [_make_order("o1"), _make_order("o2")]
    with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo, \
         patch("app.services.delivery.delivery.AccountsStorage"):
        MockRepo.return_value.get_user_orders.return_value = orders
        result = DeliveryService().get_past_orders("testuser")
    assert len(result) == 2


async def test_auto_progress():
    statuses = []
    with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo, \
         patch("app.services.delivery.delivery.AccountsStorage") as MockAcct, \
         patch("app.services.delivery.delivery.ResturantStorage") as MockRest, \
         patch("app.services.delivery.delivery.MapStorage") as MockMap, \
         patch("app.services.delivery.delivery.Notification"), \
         patch("asyncio.sleep", new_callable=AsyncMock):
        _mock_maps(MockAcct, MockRest, MockMap)
        MockAcct.return_value.get_account_info.return_value = MagicMock(email="t@t.com", username="testuser")
        MockRepo.return_value.get_order.return_value = _make_order()
        MockRepo.return_value.update_status.side_effect = lambda oid, s: (statuses.append(s), _make_order(status=s))[1]
        await DeliveryService().auto_progress("order-1")
    assert statuses == [DeliveryStatus.IN_PROCESS, DeliveryStatus.IN_TRANSIT, DeliveryStatus.DELIVERED]


def test_track_order_router():
    with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo, \
         patch("app.services.delivery.delivery.AccountsStorage"), \
         patch("app.routers.delivery.require_auth", return_value=True):
        MockRepo.return_value.get_order.return_value = _make_order()
        resp = client.get("/delivery/order-1?username=testuser&token=valid-token")
    assert resp.status_code == 200
    assert resp.json()["status"] == "Pending"


def test_past_orders_router():
    orders = [_make_order("o1"), _make_order("o2")]
    with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo, \
         patch("app.services.delivery.delivery.AccountsStorage"), \
         patch("app.routers.delivery.require_auth", return_value=True), \
         patch("app.routers.delivery.accounts_storage"):
        MockRepo.return_value.get_user_orders.return_value = orders
        resp = client.get("/delivery/past-orders/testuser?username=testuser&token=valid-token")
    assert resp.status_code == 200
    assert len(resp.json()) == 2