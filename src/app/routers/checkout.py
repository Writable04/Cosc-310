from fastapi import APIRouter, HTTPException, Depends
from app.routers.dependencies import cart_storage, require_auth, accounts_storage
from app.schemas.paymentSchema import PaymentRequest, PaymentResponse, PaymentMethod
from app.services.payment.payment import PaymentService
from app.repositories.resturant_repo import ResturantStorage
from app.repositories.map_storage import MapStorage
from typing import Optional

router = APIRouter()

DELIVERY_FEE_PER_KM = 0.05
MIN_DELIVERY_FEE    = 2.00
TAX_RATE            = 0.05


def _calculate_delivery_fee(user_address: str, restaurant_name: str) -> float:
    try:
        restaurant = ResturantStorage().find_resturant_query(restaurant_name, "name")
        if restaurant is None:
            return MIN_DELIVERY_FEE
 
        distance_km = MapStorage().calculateDeliveryDistanceKM(user_address, restaurant.restaurantAddress)
        if distance_km < 0:
            return MIN_DELIVERY_FEE
 
        return round(max(distance_km * DELIVERY_FEE_PER_KM, MIN_DELIVERY_FEE), 2)
    except Exception:
        return MIN_DELIVERY_FEE


@router.post("/{username}/{token}", response_model=PaymentResponse, dependencies=[Depends(require_auth)])
def checkout(
    username: str,
    user_id: int,
    method_id: Optional[str] = None,
    new_method: Optional[PaymentMethod] = None,
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
        user_id=user_id,
        username=username,
        restaurant=cart.restaurant,
        amount=total_before_tax,
        method_id=method_id,
        new_method=new_method,
    )
    result = ps.process_payment(payment_request)

    if result.status != "success":
        raise HTTPException(status_code=402, detail=result.message)

    return result