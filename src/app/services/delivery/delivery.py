import uuid
import asyncio
from datetime import datetime, timezone, timedelta

from app.schemas.deliverySchema import (
    DeliveryOrder,
    DeliveryStatus,
    STATUS_PROGRESSION,
)
from app.repositories.delivery_repo import DeliveryStorage
from app.repositories.storage_accounts import AccountsStorage
from app.services.notifications.notifications import Notification

STEP_DELAY = 30
TOTAL_DELIVERY_SECONDS = (len(STATUS_PROGRESSION) - 1) * STEP_DELAY


class DeliveryService:
    def __init__(self) -> None:
        self.repo = DeliveryStorage()
        self.accounts_repo = AccountsStorage()

    def start_delivery(
        self,
        user_id: int,
        username: str,
        restaurant: str,
        items: list[dict],
        total: float,
    ) -> DeliveryOrder:
        now = datetime.now(timezone.utc)
        estimated = now + timedelta(seconds=TOTAL_DELIVERY_SECONDS)

        order = DeliveryOrder(
            order_id=str(uuid.uuid4()),
            user_id=user_id,
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

    def get_order(self, order_id: str) -> DeliveryOrder | None:
        order = self.repo.get_order(order_id)
        if order is None:
            return None
        return self._with_eta(order)

    def update_status(self, order_id: str, new_status: DeliveryStatus) -> DeliveryOrder | None:
        order = self.repo.update_status(order_id, new_status)
        if order is None:
            return None
        self._notify(order, self._status_message(new_status))
        return self._with_eta(order)

    def get_past_orders(
        self,
        username: str,  # Changed from user_id: int → username: str
        restaurant: str | None = None,
        date: str | None = None,
    ) -> list[DeliveryOrder]:
        orders = self.repo.get_user_orders(username, restaurant, date)
        return [self._with_eta(o) for o in orders]

    async def auto_progress(self, order_id: str) -> None:
        for status in STATUS_PROGRESSION[1:]:
            await asyncio.sleep(STEP_DELAY)

            current = self.repo.get_order(order_id)
            if current is None or current.status == DeliveryStatus.CANCELLED:
                break

            updated = self.repo.update_status(order_id, status)
            if updated:
                self._notify(updated, self._status_message(status))

    def _with_eta(self, order: DeliveryOrder) -> DeliveryOrder:
        if order.status in (DeliveryStatus.DELIVERED, DeliveryStatus.CANCELLED):
            order.eta_seconds = None
            return order
        try:
            est = datetime.fromisoformat(order.estimated_delivery)
            now = datetime.now(timezone.utc)
            if est.tzinfo is None:
                est = est.replace(tzinfo=timezone.utc)
            order.eta_seconds = max(int((est - now).total_seconds()), 0)
        except Exception:
            order.eta_seconds = None
        return order

    def _status_message(self, status: DeliveryStatus) -> str:
        messages = {
            DeliveryStatus.PENDING:    "Your order is pending.",
            DeliveryStatus.IN_PROCESS: "Your order is being prepared.",
            DeliveryStatus.IN_TRANSIT: "Your order is out for delivery.",
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