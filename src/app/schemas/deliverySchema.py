from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class DeliveryStatus(str, Enum):
    PENDING    = "Pending"
    IN_PROCESS = "In Process"
    IN_TRANSIT = "In Transit"
    DELIVERED  = "Delivered"
    CANCELLED  = "Cancelled"


# Status progression order (Cancelled is a manual-only action)
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
    created_at: str          # ISO datetime string
    updated_at: str          # ISO datetime string
    estimated_delivery: str  # ISO datetime string (created_at + ~60s for sim)


class DeliveryStatusUpdate(BaseModel):
    status: DeliveryStatus


class DeliveryResponse(BaseModel):
    order_id: str
    restaurant: str
    items: list[dict]
    total: float
    status: DeliveryStatus
    estimated_delivery: str
    created_at: str
    updated_at: str
    eta_seconds: Optional[int] = None   # seconds until next status change