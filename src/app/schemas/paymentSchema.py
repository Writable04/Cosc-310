from pydantic import BaseModel, model_validator
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

class CheckoutRequest(BaseModel):
    method_id: Optional[str] = None
    new_method: Optional[PaymentMethod] = None

    @model_validator(mode="after")
    def check_mutually_exclusive(self) -> "CheckoutRequest":
        if self.method_id and self.new_method:
            raise ValueError(
                "Provide either a saved new card, not both."
            )
        return self

class PaymentRequest(BaseModel):
    username: str
    restaurant: Optional[str] = ""
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
    order_id: Optional[str] = None  
    subtotal: float
    tax: float
    delivery_fee: float = 0.0
    amount: float
    points_discount: float = 0.0      
    points_earned: int = 0             
    reward_points_balance: int = 0
    retry_allowed: bool = False