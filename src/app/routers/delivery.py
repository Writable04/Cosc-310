from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from app.schemas.deliverySchema import DeliveryOrder, DeliveryStatusUpdate
from app.services.delivery.delivery import DeliveryService
from app.routers.dependencies import require_auth, accounts_storage

router = APIRouter()


@router.post("/start", response_model=DeliveryOrder, status_code=201)
def start_delivery(
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: int,
    username: str,
    token: str,
    total: float,
):
    ds = DeliveryService()
    require_auth(username, token, request)

    from app.repositories.cart_repo import CartStorage

    cart = CartStorage()
    user_cart = cart.loadUserCart(str(user_id))
    items = [i.model_dump(mode="json") for i in user_cart.items] if user_cart else []

    order = ds.start_delivery(
        user_id=user_id,
        username=username,
        restaurant=user_cart.restaurant if user_cart else "",
        items=items,
        total=total,
    )

    background_tasks.add_task(ds.auto_progress, order.order_id)
    return order


@router.get("/past-orders/{user_id}", response_model=list[DeliveryOrder])
def get_past_orders(
    user_id: int,
    username: str,
    token: str,
    request: Request,
    restaurant: str | None = None,
    date: str | None = None,
):
    ds = DeliveryService()
    require_auth(username, token, request)

    account = accounts_storage.get_account_info(username)
    if account is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return ds.get_past_orders(user_id, restaurant, date)


@router.patch("/{order_id}/status", response_model=DeliveryOrder)
def update_delivery_status(
    order_id: str,
    body: DeliveryStatusUpdate,
    username: str,
    token: str,
    request: Request,
):
    ds = DeliveryService()
    require_auth(username, token, request)

    role = accounts_storage.get_account_role(username)

    if role not in ("admin",):
        raise HTTPException(
            status_code=403,
            detail="Only admin can update delivery status."
        )

    order = ds.update_status(order_id, body.status)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


@router.get("/{order_id}", response_model=DeliveryOrder)
def track_order(order_id: str, username: str, token: str, request: Request):
    ds = DeliveryService()
    require_auth(username, token, request)

    order = ds.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order