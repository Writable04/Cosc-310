import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.deliverySchema import DeliveryStatus, DeliveryOrder, STATUS_PROGRESSION
from app.services.delivery.delivery import DeliveryService

client = TestClient(app)

def _make_order(order_id="order-1", user_id=1, status=DeliveryStatus.PENDING,
                restaurant="Pizza Palace", total=49.99):
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    return DeliveryOrder(
        order_id=order_id,
        user_id=user_id,
        username="testuser",
        restaurant=restaurant,
        items=[{"name": "Pizza", "itemID": 1, "quantity": 1, "price": 49.99}],
        total=total,
        status=status,
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
        estimated_delivery=(now + timedelta(seconds=45)).isoformat(),
    )

class TestDeliveryService:

    def test_start_delivery_creates_order(self):
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                with patch("app.services.delivery.delivery.Notification"):
                    MockRepo.return_value.save_order.side_effect = lambda o: o
                    MockRepo.return_value.get_order.return_value = _make_order()
                    svc = DeliveryService()
                    order = svc.start_delivery(1, "testuser", "Pizza Palace", [], 49.99)
        assert order.status == DeliveryStatus.PENDING
        assert order.restaurant == "Pizza Palace"

    def test_get_order_returns_response(self):
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                MockRepo.return_value.get_order.return_value = _make_order()
                svc = DeliveryService()
                resp = svc.get_order("order-1")
        assert resp is not None
        assert resp.status == DeliveryStatus.PENDING

    def test_get_order_not_found_returns_none(self):
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                MockRepo.return_value.get_order.return_value = None
                svc = DeliveryService()
                resp = svc.get_order("nonexistent")
        assert resp is None

    def test_update_status_changes_status(self):
        updated = _make_order(status=DeliveryStatus.IN_PROCESS)
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                with patch("app.services.delivery.delivery.Notification"):
                    MockRepo.return_value.update_status.return_value = updated
                    svc = DeliveryService()
                    resp = svc.update_status("order-1", DeliveryStatus.IN_PROCESS)
        assert resp.status == DeliveryStatus.IN_PROCESS

    def test_get_past_orders_returns_list(self):
        orders = [_make_order("o1"), _make_order("o2")]
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                MockRepo.return_value.get_user_orders.return_value = orders
                svc = DeliveryService()
                result = svc.get_past_orders(1)
        assert len(result) == 2

    def test_past_orders_filter_by_restaurant(self):
        orders = [_make_order("o1", restaurant="Burger Barn")]
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                MockRepo.return_value.get_user_orders.return_value = orders
                svc = DeliveryService()
                result = svc.get_past_orders(1, restaurant="Burger Barn")
        assert result[0].restaurant == "Burger Barn"

    def test_eta_is_none_when_delivered(self):
        order = _make_order(status=DeliveryStatus.DELIVERED)
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                MockRepo.return_value.get_order.return_value = order
                svc = DeliveryService()
                resp = svc.get_order("order-1")
        assert resp.eta_seconds is None

    def test_eta_is_int_when_in_transit(self):
        order = _make_order(status=DeliveryStatus.IN_TRANSIT)
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                MockRepo.return_value.get_order.return_value = order
                svc = DeliveryService()
                resp = svc.get_order("order-1")
        assert isinstance(resp.eta_seconds, int)

class TestAutoProgression:

    @pytest.mark.asyncio
    async def test_auto_progress_advances_through_all_statuses(self):
        """Pending → In Process → In Transit → Delivered"""
        statuses_set = []
        order = _make_order()

        def fake_update(order_id, status):
            statuses_set.append(status)
            return _make_order(status=status)

        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                with patch("app.services.delivery.delivery.Notification"):
                    with patch("asyncio.sleep", new_callable=AsyncMock):
                        MockRepo.return_value.get_order.return_value = order
                        MockRepo.return_value.update_status.side_effect = fake_update
                        svc = DeliveryService()
                        await svc.auto_progress("order-1")

        assert statuses_set == [
            DeliveryStatus.IN_PROCESS,
            DeliveryStatus.IN_TRANSIT,
            DeliveryStatus.DELIVERED,
        ]

    @pytest.mark.asyncio
    async def test_auto_progress_stops_when_cancelled(self):
        """If order is cancelled mid-way, progression stops."""
        cancelled_order = _make_order(status=DeliveryStatus.CANCELLED)

        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    MockRepo.return_value.get_order.return_value = cancelled_order
                    MockRepo.return_value.update_status.return_value = cancelled_order
                    svc = DeliveryService()
                    await svc.auto_progress("order-1")

        MockRepo.return_value.update_status.assert_not_called()

class TestDeliveryRouter:
    def _mock_auth(self, mock_accounts, role="user"):
        from app.schemas.authenticationSchema import AccountInfo
        mock_accounts.return_value.get_account_info.return_value = AccountInfo(
            email="test@example.com", token="valid-token",
            password="hashed", username="testuser", role=role,
        )
        mock_accounts.return_value.get_account_role.return_value = role

    def test_track_order_returns_200(self):
        order = _make_order()
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                with patch("app.routers.delivery.accounts_storage") as MockAcct:
                    self._mock_auth(MockAcct)
                    MockRepo.return_value.get_order.return_value = order
                    resp = client.get(
                        "/delivery/order-1?username=testuser&token=valid-token"
                    )
        assert resp.status_code == 200
        assert resp.json()["status"] == "Pending"

    def test_track_order_not_found_returns_404(self):
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                with patch("app.routers.delivery.accounts_storage") as MockAcct:
                    self._mock_auth(MockAcct)
                    MockRepo.return_value.get_order.return_value = None
                    resp = client.get(
                        "/delivery/nonexistent?username=testuser&token=valid-token"
                    )
        assert resp.status_code == 404

    def test_admin_can_update_status(self):
        updated = _make_order(status=DeliveryStatus.CANCELLED)
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                with patch("app.routers.delivery.accounts_storage") as MockAcct:
                    self._mock_auth(MockAcct, role="admin")
                    MockRepo.return_value.update_status.return_value = updated
                    resp = client.patch(
                        "/delivery/order-1/status?username=testuser&token=valid-token",
                        json={"status": "Cancelled"},
                    )
        assert resp.status_code == 200
        assert resp.json()["status"] == "Cancelled"

    def test_regular_user_cannot_update_status(self):
        with patch("app.services.delivery.delivery.DeliveryStorage"):
            with patch("app.services.delivery.delivery.AccountsStorage"):
                with patch("app.routers.delivery.accounts_storage") as MockAcct:
                    self._mock_auth(MockAcct, role="user")
                    resp = client.patch(
                        "/delivery/order-1/status?username=testuser&token=valid-token",
                        json={"status": "Cancelled"},
                    )
        assert resp.status_code == 403

    def test_past_orders_returns_list(self):
        orders = [_make_order("o1"), _make_order("o2")]
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                with patch("app.routers.delivery.accounts_storage") as MockAcct:
                    self._mock_auth(MockAcct)
                    MockRepo.return_value.get_user_orders.return_value = orders
                    resp = client.get(
                        "/delivery/past-orders/1?username=testuser&token=valid-token"
                    )
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_past_orders_filter_by_restaurant(self):
        orders = [_make_order("o1", restaurant="Burger Barn")]
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                with patch("app.routers.delivery.accounts_storage") as MockAcct:
                    self._mock_auth(MockAcct)
                    MockRepo.return_value.get_user_orders.return_value = orders
                    resp = client.get(
                        "/delivery/past-orders/1?username=testuser&token=valid-token&restaurant=Burger+Barn"
                    )
        assert resp.status_code == 200
        assert resp.json()[0]["restaurant"] == "Burger Barn"

    def test_past_orders_filter_by_date(self):
        orders = [_make_order("o1")]
        with patch("app.services.delivery.delivery.DeliveryStorage") as MockRepo:
            with patch("app.services.delivery.delivery.AccountsStorage"):
                with patch("app.routers.delivery.accounts_storage") as MockAcct:
                    self._mock_auth(MockAcct)
                    MockRepo.return_value.get_user_orders.return_value = orders
                    resp = client.get(
                        "/delivery/past-orders/1?username=testuser&token=valid-token&date=2026-03-15"
                    )
        assert resp.status_code == 200