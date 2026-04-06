import uuid
import datetime
from app.schemas.paymentSchema import (
    PaymentMethod, SavedPaymentMethod, PaymentRequest, PaymentResponse, PaymentStatus,
)
from app.repositories.payment_repo import PaymentMethodStorage
from app.repositories.cart_repo import CartStorage
from app.repositories.storage_accounts import AccountsStorage
from app.services.notifications.notifications import Notification

TAX_RATE = 0.05

def _mask_card(card_number: str) -> str:
    return card_number[-4:] if len(card_number) >= 4 else card_number

def _is_expired(month: int, year: int) -> bool:
    return datetime.date(year, month, 1) < datetime.date.today().replace(day=1)

def _validate_payment_method(method: PaymentMethod) -> tuple[bool, str]:
    digits = method.card_number.replace(" ", "")
    if len(digits) != 16 or not digits.isdigit():
        return False, "Invalid card number format (must be 16 digits)."
    if not (1 <= method.expiry_month <= 12):
        return False, "Invalid expiry month."
    if _is_expired(method.expiry_month, method.expiry_year):
        return False, "Card has expired."
    if method.cvv == "000":
        return False, "CVV verification failed."
    if digits.endswith("0000"):
        return False, "Card was declined by the issuing bank."
    return True, "OK"

def _failed(message: str, subtotal: float, tax: float, total: float, retry: bool) -> PaymentResponse:
    return PaymentResponse(
        status=PaymentStatus.FAILED, message=message,
        subtotal=subtotal, tax=tax, delivery_fee=0.0, amount=total, retry_allowed=retry,
    )

def _stub_card(saved: SavedPaymentMethod) -> PaymentMethod:
    return PaymentMethod(
        card_holder_name=saved.card_holder_name,
        card_number="000000000000" + saved.last_four,
        expiry_month=saved.expiry_month,
        expiry_year=saved.expiry_year,
        cvv="123",
        card_type=saved.card_type,
    )


class PaymentService:
    def __init__(self) -> None:
        self.payment_repo = PaymentMethodStorage()
        self.cart_repo = CartStorage()
        self.accounts_repo = AccountsStorage()

    def add_payment_method(self, username: str, method: PaymentMethod) -> SavedPaymentMethod:
        is_valid, reason = _validate_payment_method(method)
        if not is_valid:
            raise ValueError(reason)
        saved = SavedPaymentMethod(
            method_id=str(uuid.uuid4()),
            card_holder_name=method.card_holder_name,
            last_four=_mask_card(method.card_number),
            expiry_month=method.expiry_month,
            expiry_year=method.expiry_year,
            card_type=method.card_type,
        )
        return self.payment_repo.save_method(username, saved)
 
    def get_payment_methods(self, username: str) -> list[SavedPaymentMethod]:
        return self.payment_repo.get_all_methods(username)
 
    def delete_payment_method(self, username: str, method_id: str) -> bool:
        return self.payment_repo.delete_method(username, method_id)
 
    def set_default_method(self, username: str, method_id: str) -> bool:
        return self.payment_repo.set_default(username, method_id)
 
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        subtotal = round(request.amount, 2)
        tax = round(subtotal * TAX_RATE, 2)
        total = round(subtotal + tax, 2)
 
        if subtotal <= 0:
            return _failed("Amount must be greater than 0.", subtotal, tax, total, retry=True)
        if request.new_method:
            card = request.new_method
        elif request.method_id:
            saved = self.payment_repo.get_method(request.username, request.method_id)
            if saved is None:
                return _failed("Saved payment method not found.", subtotal, tax, total, retry=True)
            card = _stub_card(saved)
        else:
            default = self.payment_repo.get_default_method(request.username)
            if default is None:
                return _failed("No payment method provided and no default method saved.", subtotal, tax, total, retry=True)
            card = _stub_card(default)
 
        is_valid, reason = _validate_payment_method(card)
        if not is_valid:
            return _failed(f"Payment failed: {reason}", subtotal, tax, total, retry=True)

        transaction_id = str(uuid.uuid4())
        self.cart_repo.clearUserCart(request.username)
        self._send_payment_notification(request.username, subtotal, tax, total, transaction_id)

        return PaymentResponse(
            status=PaymentStatus.SUCCESS,
            message="Payment successful! A confirmation has been sent to your email.",
            transaction_id=transaction_id,
            subtotal=subtotal, tax=tax, delivery_fee=0.0, amount=total,
            retry_allowed=False,
        )

    def _send_payment_notification(self, username: str, subtotal: float, tax: float, total: float, transaction_id: str) -> None:
        try:
            account = self.accounts_repo.get_account_info(username)
            if account is None:
                return
            body = (
                f"Hello {account.username},\n\n"
                f"Your payment was successful!\n\n"
                f"  Subtotal:        ${subtotal:.2f}\n"
                f"  Tax (5% GST):    ${tax:.2f}\n"
                f"  Total charged:   ${total:.2f}\n\n"
                f"Transaction ID: {transaction_id}\n\nThank you for your order!"
            )
            Notification().send_notification("Payment Confirmation", body, account.email)
        except Exception:
            pass