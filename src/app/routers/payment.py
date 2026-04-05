from fastapi import APIRouter, HTTPException
from app.schemas.paymentSchema import (
    PaymentMethod,
    PaymentResponse,
    SavedPaymentMethod,
)
from app.services.payment.payment import PaymentService
from app.routers.dependencies import accounts_storage, require_auth

router = APIRouter()
ps = PaymentService()

@router.get("/methods", response_model=list[SavedPaymentMethod])
def list_payment_methods(username: str):
    return ps.get_payment_methods(username)

@router.post("/methods", response_model=SavedPaymentMethod, status_code=201)
def add_payment_method(username: str, method: PaymentMethod):
    try:
        return ps.add_payment_method(username, method)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.delete("/methods/{method_id}", status_code=204)
def delete_payment_method(username: str, method_id: str):
    if not ps.delete_payment_method(username, method_id):
        raise HTTPException(status_code=404, detail="Payment method not found.")

@router.patch("/methods/{method_id}/default", status_code=200)
def set_default_payment_method(username: str, method_id: str):
    if not ps.set_default_method(username, method_id):
        raise HTTPException(status_code=404, detail="Payment method not found.")
    return {"detail": "Default payment method updated."}

@router.get("/reward-points", response_model=dict)
def get_reward_points(username: str):
    points = accounts_storage.get_reward_points(username)
    return {
        "username": username,
        "reward_points": points,
        "discount_value": round(points / 20, 2),
    }