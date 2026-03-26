from fastapi import APIRouter, HTTPException, Depends
from app.routers.dependencies import cart_storage, require_auth
from app.schemas.paymentSchema import PaymentRequest, PaymentResponse, PaymentMethod
from app.services.payment.payment import PaymentService
from typing import Optional

router = APIRouter()
ps = PaymentService()

@router.post("/{username}/{token}", response_model=PaymentResponse, dependencies=[Depends(require_auth)])
def checkout(
    username: str,
    user_id: int,
    method_id: Optional[str] = None,
    new_method: Optional[PaymentMethod] = None,
):
    cart = cart_storage.loadUserCart(username)

    if cart is None or len(cart.items) == 0:
        raise HTTPException(status_code=400, detail="Cart is empty. Add items before checking out.")

    amount = cart.checkout_total if cart.checkout_total > 0 else cart.subtotal
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Cart total is invalid.")

    payment_request = PaymentRequest(
        user_id=user_id,
        username=username,
        restaurant=cart.restaurant,
        amount=amount,
        method_id=method_id,
        new_method=new_method,
    )
    result = ps.process_payment(payment_request)

    if result.status != "success":
        raise HTTPException(status_code=402, detail=result.message)

    return result