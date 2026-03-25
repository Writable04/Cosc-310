from pydantic import BaseModel
from typing import Literal, Optional
from enum import Enum

class PaymentMethod(BaseModel):
    card_holder_name: str
    card_number: str
    expiry_month: int   
    expiry_year: int
    cvv: str
    card_type: Literal["credit", "debit"]

class SavedPaymentMethod(BaseModel):
    method_id: str
    card_holder_name: str
    last_four: str
    expiry_month: int
    expiry_year: int
    card_type: Literal["credit", "debit"]
    is_default: bool = False

class PaymentRequest(BaseModel):
    user_id: int
    username: str
    restaurant: str
    amount: float
    method_id: Optional[str] = None
    new_method: Optional[PaymentMethod] = None

class PaymentStatus(str, Enum):
    SUCCESS = "success"
    FAILED  = "failed"
    PENDING = "pending"

class PaymentResponse(BaseModel):
    status: PaymentStatus
    message: str
    transaction_id: Optional[str] = None
    subtotal: float
    tax: float
    amount: float
    retry_allowed: bool = False