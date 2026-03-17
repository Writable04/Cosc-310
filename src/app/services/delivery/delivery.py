import uuid
import random
import asyncio
from datetime import datetime, timezone, timedelta

from app.schemas.deliverySchema import (
    DeliveryOrder,
    DeliveryStatus,
    DeliveryResponse,
    STATUS_PROGRESSION,
)
from app.repositories.delivery_repo import DeliveryStorage
from app.repositories.storage_accounts import AccountsStorage
from app.services.notifications.notifications import Notification

PROGRESSION_MIN = 10
PROGRESSION_MAX = 15

TOTAL_DELIVERY_SECONDS = (len(STATUS_PROGRESSION) - 1) * PROGRESSION_MAX

class DeliveryService:
    def __init__(self) -> None:
        self.delivery_repo = DeliveryStorage()
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
        self.delivery_repo.save_order(order)
        self._notify(order, "Your order has been placed and is Pending.")
        return order

    def get_order(self, order_id: str) -> DeliveryResponse | None:
        order = self.delivery_repo.get_order(order_id)
        if order is None:
            return None
        return self._to_response(order)

    def update_status(
        self, order_id: str, new_status: DeliveryStatus
    ) -> DeliveryResponse | None:
        order = self.delivery_repo.update_status(order_id, new_status)
        if order is None:
            return None
        self._notify(order, f"Your order status has been updated to: {new_status.value}")
        return self._to_response(order)

    def get_past_orders(
        self,
        user_id: int,
        restaurant: str | None = None,
        date: str | None = None,
    ) -> list[DeliveryResponse]:
        orders = self.delivery_repo.get_user_orders(user_id, restaurant, date)
        return [self._to_response(o) for o in orders]

    async def auto_progress(self, order_id: str) -> None:
        for i in range(1, len(STATUS_PROGRESSION)):
            delay = random.randint(PROGRESSION_MIN, PROGRESSION_MAX)
            await asyncio.sleep(delay)

            current = self.delivery_repo.get_order(order_id)
            if current is None or current.status == DeliveryStatus.CANCELLED:
                break

            next_status = STATUS_PROGRESSION[i]
            order = self.delivery_repo.update_status(order_id, next_status)
            if order:
                msg = self._status_message(next_status)
                self._notify(order, msg)

    def _to_response(self, order: DeliveryOrder) -> DeliveryResponse:
        """Build a DeliveryResponse with a live ETA in seconds."""
        eta = None
        if order.status not in (DeliveryStatus.DELIVERED, DeliveryStatus.CANCELLED):
            try:
                est = datetime.fromisoformat(order.estimated_delivery)
                now = datetime.now(timezone.utc)
                # Make est timezone-aware if needed
                if est.tzinfo is None:
                    est = est.replace(tzinfo=timezone.utc)
                delta = int((est - now).total_seconds())
                eta = max(delta, 0)
            except Exception:
                eta = None

        return DeliveryResponse(
            order_id=order.order_id,
            restaurant=order.restaurant,
            items=order.items,
            total=order.total,
            status=order.status,
            estimated_delivery=order.estimated_delivery,
            created_at=order.created_at,
            updated_at=order.updated_at,
            eta_seconds=eta,
        )

    def _status_message(self, status: DeliveryStatus) -> str:
        messages = {
            DeliveryStatus.PENDING:    "Your order has been placed and is Pending.",
            DeliveryStatus.IN_PROCESS: "Your order is now being prepared!",
            DeliveryStatus.IN_TRANSIT: "Your order is out for delivery and on its way!",
            DeliveryStatus.DELIVERED:  "Your order has been delivered. Enjoy your meal!",
            DeliveryStatus.CANCELLED:  "Your order has been cancelled.",
        }
        return messages.get(status, f"Order status updated to {status.value}.")

    def _notify(self, order: DeliveryOrder, message: str) -> None:
        """Send email notification; silently skip on failure."""
        try:
            account = self.accounts_repo.get_account_info(order.username)
            if account is None:
                return
            notifier = Notification()
            subject = f"Order Update – {order.status.value}"
            body = (
                f"Hello {order.username},\n\n"
                f"{message}\n\n"
                f"Order ID : {order.order_id}\n"
                f"Restaurant: {order.restaurant}\n"
                f"Total     : ${order.total:.2f}\n\n"
                "— Food Delivery Team"
            )
            notifier.send_notification(subject, body, account.email)
        except Exception:
            pass