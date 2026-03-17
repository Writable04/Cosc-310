from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from app.schemas.deliverySchema import DeliveryResponse, DeliveryStatusUpdate, DeliveryStatus
from app.services.delivery.delivery import DeliveryService
from app.routers.dependencies import require_auth, accounts_storage

router = APIRouter()
ds = DeliveryService()


# ---------------------------------------------------------------------------
# Start a delivery (called after successful payment)
# F5SR1
# ---------------------------------------------------------------------------

@router.post("/start", response_model=DeliveryResponse, status_code=201)
def start_delivery(
    background_tasks: BackgroundTasks,
    user_id: int,
    username: str,
    token: str,
    restaurant: str,
    total: float,
):
    """
    Create a new delivery order and begin auto-progression in the background.
    Requires a valid user token.
    """
    # Verify the user is authenticated
    from app.services.authentication.auth import Authentication
    auth = Authentication(accounts_storage)
    auth.authenticate(username, token)

    # Load cart items for the order record
    from app.repositories.cart_repo import CartStorage
    cart = CartStorage()
    user_cart = cart.loadUserCart(user_id)
    items = [i.model_dump(mode="json") for i in user_cart.items] if user_cart else []

    order = ds.start_delivery(
        user_id=user_id,
        username=username,
        restaurant=restaurant,
        items=items,
        total=total,
    )

    # Kick off auto-progression as a background task
    background_tasks.add_task(ds.auto_progress, order.order_id)

    return ds.get_order(order.order_id)


# ---------------------------------------------------------------------------
# Track a single order  (F5US1, F5US2)
# ---------------------------------------------------------------------------

@router.get("/{order_id}", response_model=DeliveryResponse)
def track_order(order_id: str, username: str, token: str):
    """
    Get the current delivery status and ETA for an order.
    The requesting user must be authenticated.
    """
    from app.services.authentication.auth import Authentication
    auth = Authentication(accounts_storage)
    auth.authenticate(username, token)

    order = ds.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


# ---------------------------------------------------------------------------
# Manual status update – admin/driver only  (F5SR2)
# ---------------------------------------------------------------------------

@router.patch("/{order_id}/status", response_model=DeliveryResponse)
def update_delivery_status(
    order_id: str,
    body: DeliveryStatusUpdate,
    username: str,
    token: str,
):
    """
    Manually update delivery status (admin or driver role only).
    Can also be used to cancel an order.
    """
    from app.services.authentication.auth import Authentication
    auth = Authentication(accounts_storage)
    auth.authenticate(username, token)

    role = accounts_storage.get_account_role(username)
    if role not in ("admin", "driver"):
        raise HTTPException(status_code=403, detail="Only admin or driver can update delivery status.")

    order = ds.update_status(order_id, body.status)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


# ---------------------------------------------------------------------------
# Past orders – logged-in user  (F5US3)
# ---------------------------------------------------------------------------

@router.get("/past-orders/{user_id}", response_model=list[DeliveryResponse])
def get_past_orders(
    user_id: int,
    username: str,
    token: str,
    restaurant: str | None = None,
    date: str | None = None,
):
    """
    Return all past orders for the logged-in user.
    Optional filters:
      - restaurant: filter by restaurant name (partial match)
      - date: filter by date in YYYY-MM-DD format
    """
    from app.services.authentication.auth import Authentication
    auth = Authentication(accounts_storage)
    auth.authenticate(username, token)

    # Users can only see their own orders
    account = accounts_storage.get_account_info(username)
    if account is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return ds.get_past_orders(user_id, restaurant, date)