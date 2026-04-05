from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.routers.dependencies import cart_storage, require_auth, accounts_storage
from app.schemas.paymentSchema import CheckoutRequest, PaymentRequest, PaymentResponse
from app.services.payment.payment import PaymentService
from app.services.delivery.delivery import DeliveryService
from app.repositories.resturant_repo import ResturantStorage
from app.repositories.map_storage import MapStorage

router = APIRouter()

DELIVERY_FEE_PER_KM = 0.50
MIN_DELIVERY_FEE    = 2.00


def _calculate_delivery_fee(user_address: str, restaurant_name: str) -> float:
    try:
        repo = ResturantStorage()

        # Try lookup by name first, then fall back to restaurant_id
        # This handles cases where cart.restaurant stores a name or an id
        restaurant = repo.find_resturant_query(restaurant_name, "name")
        if restaurant is None:
            restaurant = repo.find_resturant_query(restaurant_name, "restaurant_id")
        if restaurant is None:
            return MIN_DELIVERY_FEE

        distance_km = MapStorage().calculateDeliveryDistanceKM(user_address, restaurant.restaurantAddress)
        if distance_km < 0:
            return MIN_DELIVERY_FEE

        fee = round(max(distance_km * DELIVERY_FEE_PER_KM, MIN_DELIVERY_FEE), 2)
        print(f"Delivery fee: {fee} (distance: {distance_km:.2f} km from '{user_address}' to '{restaurant.restaurantAddress}')")
        return fee
    except Exception as e:
        print(f"Delivery fee calculation error: {e}")
        return MIN_DELIVERY_FEE


@router.post("/{username}/{token}", response_model=PaymentResponse, dependencies=[Depends(require_auth)])
def checkout(
    username: str,
    background_tasks: BackgroundTasks,
    body: CheckoutRequest = CheckoutRequest(),
):
    ps = PaymentService()

    cart = cart_storage.loadUserCart(username)
    if cart is None or len(cart.items) == 0:
        raise HTTPException(status_code=400, detail="Cart is empty. Add items before checking out.")

    cart_amount = cart.checkout_total if cart.checkout_total > 0 else cart.subtotal
    if cart_amount <= 0:
        raise HTTPException(status_code=400, detail="Cart total is invalid.")

    user_address = accounts_storage.get_address(username)
    if user_address:
        delivery_fee = _calculate_delivery_fee(user_address, cart.restaurant)
    else:
        delivery_fee = MIN_DELIVERY_FEE

    total_before_tax = round(cart_amount + delivery_fee, 2)

    payment_request = PaymentRequest(
        username=username,
        restaurant=cart.restaurant,
        amount=total_before_tax,
        method_id=body.method_id,
        new_method=body.new_method,
    )
    result = ps.process_payment(payment_request)

    if result.status != "success":
        raise HTTPException(status_code=402, detail=result.message)

    result.delivery_fee = delivery_fee

    ds = DeliveryService()
    items = [i.model_dump(mode="json") for i in cart.items]
    order = ds.start_delivery(
        user_id=0,
        username=username,
        restaurant=cart.restaurant,
        items=items,
        total=result.amount,
    )
    background_tasks.add_task(ds.auto_progress, order.order_id)

    result.order_id = order.order_id  # return order_id so frontend can track delivery
    return result