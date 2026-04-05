import uuid
import datetime
from app.schemas.paymentSchema import (
    PaymentMethod,
    SavedPaymentMethod,
    PaymentRequest,
    PaymentResponse,
    PaymentStatus,
)
from app.repositories.payment_repo import PaymentMethodStorage
from app.repositories.cart_repo import CartStorage
from app.repositories.storage_accounts import AccountsStorage
from app.services.notifications.notifications import Notification

TAX_RATE = 0.05
MAX_ORDER_AMOUNT = 500.00

def _mask_card(card_number: str) -> str:
    return card_number[-4:] if len(card_number) >= 4 else card_number

def _is_expired(month: int, year: int) -> bool:
    now = datetime.date.today()
    expiry = datetime.date(year, month, 1)
    return expiry < now.replace(day=1)

def _validate_payment_method(method: PaymentMethod) -> tuple[bool, str]:
    card_digits = method.card_number.replace(" ", "")
    if len(card_digits) != 16 or not card_digits.isdigit():
        return False, "Invalid card number format (must be 16 digits)."
    if not (1 <= method.expiry_month <= 12):
        return False, "Invalid expiry month."
    if _is_expired(method.expiry_month, method.expiry_year):
        return False, "Card has expired."
    if method.cvv == "000":
        return False, "CVV verification failed."
    if card_digits.endswith("0000"):
        return False, "Card was declined by the issuing bank."
    return True, "OK"

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
            return PaymentResponse(
                status=PaymentStatus.FAILED,
                message="Amount must be greater than 0.",
                subtotal=subtotal, tax=tax, delivery_fee=0.0, amount=total,
                retry_allowed=True,
            )

        if total > MAX_ORDER_AMOUNT:
            return PaymentResponse(
                status=PaymentStatus.FAILED,
                message=f"Order total ${total:.2f} (incl. tax) exceeds the maximum of ${MAX_ORDER_AMOUNT:.2f}.",
                subtotal=subtotal, tax=tax, delivery_fee=0.0, amount=total,
                retry_allowed=False,
            )

        card_to_validate: PaymentMethod | None = None

        if request.new_method:
            card_to_validate = request.new_method
        elif request.method_id:
            # Now keyed by username (str)
            saved = self.payment_repo.get_method(request.username, request.method_id)
            if saved is None:
                return PaymentResponse(
                    status=PaymentStatus.FAILED,
                    message="Saved payment method not found.",
                    subtotal=subtotal, tax=tax, delivery_fee=0.0, amount=total,
                    retry_allowed=True,
                )
            card_to_validate = PaymentMethod(
                card_holder_name=saved.card_holder_name,
                card_number="000000000000" + saved.last_four,
                expiry_month=saved.expiry_month,
                expiry_year=saved.expiry_year,
                cvv="123",
                card_type=saved.card_type,
            )
        else:
            default = self.payment_repo.get_default_method(request.username)
            if default is None:
                return PaymentResponse(
                    status=PaymentStatus.FAILED,
                    message="No payment method provided and no default method saved.",
                    subtotal=subtotal, tax=tax, delivery_fee=0.0, amount=total,
                    retry_allowed=True,
                )
            card_to_validate = PaymentMethod(
                card_holder_name=default.card_holder_name,
                card_number="000000000000" + default.last_four,
                expiry_month=default.expiry_month,
                expiry_year=default.expiry_year,
                cvv="123",
                card_type=default.card_type,
            )

        is_valid, reason = _validate_payment_method(card_to_validate)
        if not is_valid:
            return PaymentResponse(
                status=PaymentStatus.FAILED,
                message=f"Payment failed: {reason}",
                subtotal=subtotal, tax=tax, delivery_fee=0.0, amount=total,
                retry_allowed=True,
            )

        transaction_id = str(uuid.uuid4())
        # Clear cart by username (str) now that payment repo is username-keyed
        self.cart_repo.clearUserCart(request.username)
        self._send_payment_notification(request.username, subtotal, tax, total, transaction_id)

        return PaymentResponse(
            status=PaymentStatus.SUCCESS,
            message="Payment successful! A confirmation has been sent to your email.",
            transaction_id=transaction_id,
            subtotal=subtotal,
            tax=tax,
            delivery_fee=0.0,
            amount=total,
            retry_allowed=False,
        )

    def _send_payment_notification(self, username: str, subtotal: float, tax: float, total: float, transaction_id: str) -> None:
        try:
            account = self.accounts_repo.get_account_info(username)
            if account is None:
                print(f"Notification error: account not found for username {username}")
                return
            notifier = Notification()
            subject = "Payment Confirmation"
            body = (
                f"Hello {account.username},\n\n"
                f"Your payment was successful!\n\n"
                f"  Subtotal:        ${subtotal:.2f}\n"
                f"  Tax (5% GST):    ${tax:.2f}\n"
                f"  Total charged:   ${total:.2f}\n\n"
                f"Transaction ID: {transaction_id}\n\n"
                "Thank you for your order!"
            )
            notifier.send_notification(subject, body, account.email)
        except Exception as e:
            print(f"Notification error: {e}")