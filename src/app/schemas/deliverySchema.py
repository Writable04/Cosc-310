from pydantic import BaseModel
from typing import Optional
from enum import Enum


class DeliveryStatus(str, Enum):
    PENDING    = "Pending"
    IN_PROCESS = "In Process"
    IN_TRANSIT = "In Transit"
    DELIVERED  = "Delivered"
    CANCELLED  = "Cancelled"


STATUS_PROGRESSION = [
    DeliveryStatus.PENDING,
    DeliveryStatus.IN_PROCESS,
    DeliveryStatus.IN_TRANSIT,
    DeliveryStatus.DELIVERED,
]

class DeliveryOrder(BaseModel):
    order_id: str
    user_id: int
    username: str
    restaurant: str
    items: list[dict]
    total: float
    status: DeliveryStatus = DeliveryStatus.PENDING
    eta_seconds: Optional[int] = None
    created_at: str = ""
    updated_at: str = ""


class DeliveryStatusUpdate(BaseModel):
    status: DeliveryStatus