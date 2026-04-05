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
    username: str
    restaurant: str
    items: list[dict]
    total: float
    status: DeliveryStatus = DeliveryStatus.PENDING
    eta_seconds: Optional[int] = None
    created_at: str = ""
    updated_at: str = ""
    estimated_delivery: str = ""


class DeliveryStatusUpdate(BaseModel):
    status: DeliveryStatus

class OrderStatusResponse(BaseModel):
    order_id: str
    status: DeliveryStatus
    status_label: str
    eta_seconds: Optional[int]
    eta_minutes: Optional[int]
    estimated_delivery: Optional[str] = None

class OrderSummaryResponse(BaseModel):
    order_id: str
    restaurant: str
    status: DeliveryStatus
    status_label: str
    total: float
    delivery_fee: float = 0.0
    eta_seconds: Optional[int]
    eta_minutes: Optional[int]
    created_at: str
    estimated_delivery: Optional[str] = None