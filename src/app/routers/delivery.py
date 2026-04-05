import math
from fastapi import APIRouter, Request
from typing import Optional
from app.schemas.deliverySchema import (
    DeliveryOrder, DeliveryStatus, DeliveryStatusUpdate,
    OrderStatusResponse, OrderSummaryResponse,
)
from app.services.delivery.delivery import DeliveryService, _format_estimated_delivery
from app.routers.dependencies import require_auth, accounts_storage

router = APIRouter()

STATUS_LABELS = {
    DeliveryStatus.PENDING:    "Order received, waiting to be confirmed",
    DeliveryStatus.IN_PROCESS: "Your order is being prepared",
    DeliveryStatus.IN_TRANSIT: "Your order is out for delivery",
    DeliveryStatus.DELIVERED:  "Your order has been delivered",
    DeliveryStatus.CANCELLED:  "Your order has been cancelled",
}

def _eta_minutes(eta_seconds: Optional[int]) -> Optional[int]:
    return math.ceil(eta_seconds / 60) if eta_seconds is not None else None


@router.get("/{order_id}/status", response_model=OrderStatusResponse)
def get_order_status(order_id: str, username: str, token: str, request: Request):
    ds = DeliveryService()
    require_auth(username, token, request)
    order = ds.get_order(order_id)
    return OrderStatusResponse(
        order_id=order.order_id,
        status=order.status,
        status_label=STATUS_LABELS.get(order.status, order.status.value),
        eta_seconds=order.eta_seconds,
        eta_minutes=_eta_minutes(order.eta_seconds),
        estimated_delivery=_format_estimated_delivery(order.estimated_delivery),
    )


@router.get("/{order_id}/summary", response_model=OrderSummaryResponse)
def get_order_summary(order_id: str, username: str, token: str, request: Request):
    ds = DeliveryService()
    require_auth(username, token, request)
    order = ds.get_order(order_id)
    return OrderSummaryResponse(
        order_id=order.order_id,
        restaurant=order.restaurant,
        status=order.status,
        status_label=STATUS_LABELS.get(order.status, order.status.value),
        total=order.total,
        eta_seconds=order.eta_seconds,
        eta_minutes=_eta_minutes(order.eta_seconds),
        created_at=order.created_at,
        estimated_delivery=_format_estimated_delivery(order.estimated_delivery),
    )


@router.get("/past-orders/{username}", response_model=list[DeliveryOrder])
def get_past_orders(username: str, token: str, request: Request):
    ds = DeliveryService()
    require_auth(username, token, request)
    return ds.get_past_orders(username)


@router.patch("/{order_id}/status", response_model=DeliveryOrder)
def update_delivery_status(order_id: str, body: DeliveryStatusUpdate, username: str, token: str, request: Request):
    ds = DeliveryService()
    require_auth(username, token, request)
    return ds.update_status(order_id, body.status)


@router.get("/{order_id}", response_model=DeliveryOrder)
def track_order(order_id: str, username: str, token: str, request: Request):
    ds = DeliveryService()
    require_auth(username, token, request)
    return ds.get_order(order_id)