import uuid
import time
from datetime import datetime, timezone

from app.schemas.deliverySchema import (
    DeliveryOrder,
    DeliveryStatus,
    STATUS_PROGRESSION,
)
from app.repositories.delivery_repo import DeliveryStorage
from app.repositories.storage_accounts import AccountsStorage
from app.repositories.map_storage import MapStorage
from app.services.notifications.notifications import Notification

class DeliveryService:
    def __init__(self) -> None:
        self.repo = DeliveryStorage()
        self.accounts_repo = AccountsStorage()
        self.maps = MapStorage()

    def start_delivery(
        self,
        user_id: int,
        username: str,
        restaurant: str,
        restaurant_address: str,
        user_address: str,
        items: list[dict],
        total: float,
    ) -> DeliveryOrder:
        duration_mins = self.maps.calculateDeliveryTimeMins(user_address, restaurant_address)
        eta_seconds = duration_mins * 60 if duration_mins > 0 else 600

        now = datetime.now(timezone.utc).isoformat()
        order = DeliveryOrder(
            order_id=str(uuid.uuid4()),
            user_id=user_id,
            username=username,
            restaurant=restaurant,
            items=items,
            total=total,
            status=DeliveryStatus.PENDING,
            eta_seconds=eta_seconds,
            created_at=now,
            updated_at=now,
        )
        self.repo.save_order(order)
        self._notify(order, "Your order is pending.")
        return order

    def get_order(self, order_id: str) -> DeliveryOrder | None:
        return self.repo.get_order(order_id)

    def update_status(self, order_id: str, new_status: DeliveryStatus) -> DeliveryOrder | None:
        order = self.repo.update_status(order_id, new_status)
        if order is None:
            return None
        self._notify(order, self._status_message(new_status))
        return order

    def get_past_orders(
        self,
        user_id: int,
        restaurant: str | None = None,
        date: str | None = None,
    ) -> list[DeliveryOrder]:
        return self.repo.get_user_orders(user_id, restaurant, date)

    def auto_progress(self, order_id: str) -> None:
        order = self.repo.get_order(order_id)
        if order is None:
            return

        steps = len(STATUS_PROGRESSION) - 1  
        step_delay = 30

        for status in STATUS_PROGRESSION[1:]: 
            time.sleep(step_delay)

            current = self.repo.get_order(order_id)
            if current is None or current.status == DeliveryStatus.CANCELLED:
                break

            updated = self.repo.update_status(order_id, status)
            if updated:
                self._notify(updated, self._status_message(status))

    def _status_message(self, status: DeliveryStatus) -> str:
        messages = {
            DeliveryStatus.PENDING:    "Your order is Pending.",
            DeliveryStatus.IN_PROCESS: "Your order is getting prepared",
            DeliveryStatus.IN_TRANSIT: "Your order is out for delivery",
            DeliveryStatus.DELIVERED:  "Your order has been delivered.",
            DeliveryStatus.CANCELLED:  "Your order has been cancelled.",
        }
        return messages.get(status, f"Order status updated to {status.value}.")

    def _notify(self, order: DeliveryOrder, message: str) -> None:
        try:
            account = self.accounts_repo.get_account_info(order.username)
            if account is None:
                return
            subject = f"Order Update – {order.status.value}"
            body = (
                f"Hello {order.username},\n\n"
                f"{message}\n\n"
                f"Order ID  : {order.order_id}\n"
                f"Restaurant: {order.restaurant}\n"
                f"Total     : ${order.total:.2f}\n\n"
                "— Food Delivery Team"
            )
            Notification().send_notification(subject, body, account.email)
        except Exception:
            pass