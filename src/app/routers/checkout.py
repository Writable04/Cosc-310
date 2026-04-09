import math
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
POINTS_TO_DOLLAR    = 20  # 20 points = $1 discount


def _calculate_delivery_fee(user_address: str, restaurant_name: str) -> float:
    try:
        repo = ResturantStorage()
        restaurant = repo.find_resturant_query(restaurant_name, "name")
        if restaurant is None:
            restaurant = repo.find_resturant_query(restaurant_name, "restaurant_id")
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
 
    # users choice to redeem the points
    points_discount = 0.0
    points_used = 0
    rollover_points = 0
    if accounts_storage.get_redeem_choice(username):
        current_points = accounts_storage.get_reward_points(username)
        if current_points > 0:
            full_discount = round(current_points / POINTS_TO_DOLLAR, 2)
 
            if full_discount >= cart_amount:
                # Points> subtotal = rollover points for the next purchase
                points_discount = cart_amount
                points_used = math.ceil(cart_amount * POINTS_TO_DOLLAR)
                rollover_points = current_points - points_used
                accounts_storage.deduct_reward_points(username, current_points)
                accounts_storage.add_reward_points(username, rollover_points)
            else:
                # Points partially cover the subtotal = use all points
                points_discount = full_discount
                points_used = current_points
                accounts_storage.deduct_reward_points(username, points_used)
 
    # Delivery fee calculated on original cart amount
    user_address = accounts_storage.get_address(username)
    delivery_fee = _calculate_delivery_fee(user_address, cart.restaurant) if user_address else MIN_DELIVERY_FEE
 
    # making sure the tax is based on item subtotal only
    payment_request = PaymentRequest(
        username=username,
        restaurant=cart.restaurant,
        amount=cart_amount,
        method_id=body.method_id,
        new_method=body.new_method,
    )
    result = ps.process_payment(payment_request)
 
    if result.status != "success":
        # Refund points if payment failed
        if points_used > 0:
            accounts_storage.add_reward_points(username, points_used)
        raise HTTPException(status_code=402, detail=result.message)
 
    # Earn 1 point per $1 of subtotal
    points_earned = math.floor(cart_amount)
    new_balance = accounts_storage.add_reward_points(username, points_earned)
 
    result.subtotal = cart_amount  # cart items total
    result.delivery_fee = delivery_fee
    result.amount = round(result.amount + delivery_fee - points_discount, 2)
    result.points_discount = points_discount
    result.points_earned = points_earned
    result.reward_points_balance = new_balance
 
    ds = DeliveryService()
    items = [i.model_dump(mode="json") for i in cart.items]
    order = ds.start_delivery(
        username=username,
        restaurant=cart.restaurant,
        items=items,
        total=result.amount,
    )
    background_tasks.add_task(ds.auto_progress, order.order_id)
    result.order_id = order.order_id
    return result