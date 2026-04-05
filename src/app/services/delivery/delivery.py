import uuid
import asyncio
from datetime import datetime, timezone, timedelta

from app.schemas.deliverySchema import DeliveryOrder, DeliveryStatus, STATUS_PROGRESSION
from app.repositories.delivery_repo import DeliveryStorage
from app.repositories.storage_accounts import AccountsStorage
from app.repositories.resturant_repo import ResturantStorage
from app.repositories.map_storage import MapStorage
from app.services.notifications.notifications import Notification

IN_PROCESS_SECONDS = 600  # 10 min prep time


def _get_transit_seconds(username: str, restaurant_name: str) -> int:
    user_address = AccountsStorage().get_address(username)
    restaurant = ResturantStorage().find_resturant_query(restaurant_name, "name")
    minutes = MapStorage().calculateDeliveryTimeMins(restaurant.restaurantAddress, user_address)
    return minutes * 60


def _format_estimated_delivery(estimated_delivery: str) -> str:
    from datetime import datetime, timezone
    import time
    try:
        est = datetime.fromisoformat(estimated_delivery)
        if est.tzinfo is None:
            est = est.replace(tzinfo=timezone.utc)
        # Convert to local time
        local_offset = datetime.now() - datetime.utcnow()
        est_local = est.replace(tzinfo=None) + local_offset
        return est_local.strftime("%I:%M %p")  #12:21 PM"
    except Exception:
        return estimated_delivery


class DeliveryService:
    def __init__(self) -> None:
        self.repo = DeliveryStorage()
        self.accounts_repo = AccountsStorage()

    def start_delivery(self, username: str, restaurant: str, items: list[dict], total: float) -> DeliveryOrder:
        now = datetime.now(timezone.utc)
        transit_seconds = _get_transit_seconds(username, restaurant)
        estimated = now + timedelta(seconds=IN_PROCESS_SECONDS + transit_seconds)

        order = DeliveryOrder(
            order_id=str(uuid.uuid4()),
            username=username,
            restaurant=restaurant,
            items=items,
            total=total,
            status=DeliveryStatus.PENDING,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            estimated_delivery=estimated.isoformat(),
        )
        self.repo.save_order(order)
        self._notify(order, "Your order is pending.")
        return order

    def get_order(self, order_id: str) -> DeliveryOrder:
        return self._with_eta(self.repo.get_order(order_id))

    def update_status(self, order_id: str, new_status: DeliveryStatus) -> DeliveryOrder:
        order = self.repo.update_status(order_id, new_status)
        self._notify(order, self._status_message(new_status))
        return self._with_eta(order)

    def get_past_orders(self, username: str) -> list[DeliveryOrder]:
        return [self._with_eta(o) for o in self.repo.get_user_orders(username)]

    async def auto_progress(self, order_id: str) -> None:
        transit_seconds = _get_transit_seconds(
            self.repo.get_order(order_id).username,
            self.repo.get_order(order_id).restaurant,
        )
        stage_delays = {
            DeliveryStatus.IN_PROCESS: IN_PROCESS_SECONDS,
            DeliveryStatus.IN_TRANSIT: transit_seconds,
            DeliveryStatus.DELIVERED:  0,
        }
        for status in STATUS_PROGRESSION[1:]:
            await asyncio.sleep(stage_delays.get(status, 0))
            updated = self.repo.update_status(order_id, status)
            self._notify(updated, self._status_message(status))

    def _with_eta(self, order: DeliveryOrder) -> DeliveryOrder:
        if order.status in (DeliveryStatus.DELIVERED, DeliveryStatus.CANCELLED):
            order.eta_seconds = None
            return order
        est = datetime.fromisoformat(order.estimated_delivery)
        now = datetime.now(timezone.utc)
        if est.tzinfo is None:
            est = est.replace(tzinfo=timezone.utc)
        order.eta_seconds = max(int((est - now).total_seconds()), 0)
        return order

    def _status_message(self, status: DeliveryStatus) -> str:
        return {
            DeliveryStatus.PENDING:    "Your order is pending.",
            DeliveryStatus.IN_PROCESS: "Your order is being prepared.",
            DeliveryStatus.IN_TRANSIT: "Your order is out for delivery.",
            DeliveryStatus.DELIVERED:  "Your order has been delivered.",
            DeliveryStatus.CANCELLED:  "Your order has been cancelled.",
        }.get(status, f"Order status updated to {status.value}.")

    def _notify(self, order: DeliveryOrder, message: str) -> None:
        account = self.accounts_repo.get_account_info(order.username)
        est_display = _format_estimated_delivery(order.estimated_delivery)
        Notification().send_notification(
            subject=f"Order Update – {order.status.value}",
            message=(
                f"Hello {order.username},\n\n{message}\n\n"
                f"Order ID          : {order.order_id}\n"
                f"Restaurant        : {order.restaurant}\n"
                f"Estimated Delivery: {est_display}\n"
                f"Total             : ${order.total:.2f}\n\n"
                "— Food Delivery Team"
            ),
            receiver_email=account.email,
        )