from pathlib import Path
from app.repositories.storage_base import Storage
from app.schemas.deliverySchema import DeliveryOrder, DeliveryStatus


class DeliveryStorage(Storage[dict]):
    def __init__(self, path: Path | None = None) -> None:
        path = path or Path(__file__).parent.parent / "data" / "orders.json"
        super().__init__(path)

    def save_order(self, order: DeliveryOrder) -> DeliveryOrder:
        self.write(order.order_id, order.model_dump(mode="json"))

        user_key = f"user:{order.user_id}"
        existing = self.read(user_key)
        order_ids: list = existing if isinstance(existing, list) else []
        if order.order_id not in order_ids:
            order_ids.append(order.order_id)
        self.write(user_key, order_ids)

        return order

    def update_status(self, order_id: str, status: DeliveryStatus) -> DeliveryOrder | None:
        from datetime import datetime, timezone
        data = self.read(order_id)
        if data is None:
            return None
        data["status"] = status.value
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.write(order_id, data)
        return DeliveryOrder.model_validate(data)

    def get_order(self, order_id: str) -> DeliveryOrder | None:
        data = self.read(order_id)
        if data is None or not isinstance(data, dict):
            return None
        return DeliveryOrder.model_validate(data)

    def get_user_orders(
        self,
        user_id: int,
        restaurant: str | None = None,
        date: str | None = None,          
    ) -> list[DeliveryOrder]:
        user_key = f"user:{user_id}"
        order_ids = self.read(user_key)
        if not order_ids:
            return []

        orders = []
        for oid in order_ids:
            order = self.get_order(oid)
            if order is None:
                continue
            if restaurant and restaurant.lower() not in order.restaurant.lower():
                continue
            if date and not order.created_at.startswith(date):
                continue

            orders.append(order)

        orders.sort(key=lambda o: o.created_at, reverse=True)
        return orders