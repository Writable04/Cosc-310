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


MAX_ORDER_AMOUNT = 500.00

def _mask_card(card_number: str) -> str:
    return card_number[-4:] if len(card_number) >= 4 else card_number

def _is_expired(month: int, year: int) -> bool:
    now = datetime.date.today()
    expiry = datetime.date(year, month, 1)
    first_of_this_month = now.replace(day=1)
    return expiry < first_of_this_month

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

    def add_payment_method(
        self, user_id: int, method: PaymentMethod
    ) -> SavedPaymentMethod:
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
        return self.payment_repo.save_method(user_id, saved)

    def get_payment_methods(self, user_id: int) -> list[SavedPaymentMethod]:
        return self.payment_repo.get_all_methods(user_id)

    def delete_payment_method(self, user_id: int, method_id: str) -> bool:
        return self.payment_repo.delete_method(user_id, method_id)

    def set_default_method(self, user_id: int, method_id: str) -> bool:
        return self.payment_repo.set_default(user_id, method_id)

    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        if request.amount <= 0:
            return PaymentResponse(
                status=PaymentStatus.FAILED,
                message="Insufficient balance, must be greater than 0",
                amount=request.amount,
                retry_allowed=True,
    )

        if request.amount > MAX_ORDER_AMOUNT:
            return PaymentResponse(
                status=PaymentStatus.FAILED,
                message=(
                    f"Order total ${request.amount:.2f} exceeds the maximum "
                    f"allowed single-order amount of ${MAX_ORDER_AMOUNT:.2f}."
                ),
                amount=request.amount,
                retry_allowed=False,
            )

        card_to_validate: PaymentMethod | None = None

        if request.new_method:
            card_to_validate = request.new_method

        elif request.method_id:
            saved = self.payment_repo.get_method(request.user_id, request.method_id)
            if saved is None:
                return PaymentResponse(
                    status=PaymentStatus.FAILED,
                    message="Saved payment method not found.",
                    amount=request.amount,
                    retry_allowed=True,
                )
            card_to_validate = PaymentMethod(
                card_holder_name=saved.card_holder_name,
                card_number="0000" * 3 + saved.last_four,
                expiry_month=saved.expiry_month,
                expiry_year=saved.expiry_year,
                cvv="123",
                card_type=saved.card_type,
            )

        else:
            default = self.payment_repo.get_default_method(request.user_id)
            if default is None:
                return PaymentResponse(
                    status=PaymentStatus.FAILED,
                    message="No payment method provided and no default method saved.",
                    amount=request.amount,
                    retry_allowed=True,
                )
            card_to_validate = PaymentMethod(
                card_holder_name=default.card_holder_name,
                card_number="0000" * 3 + default.last_four,
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
                amount=request.amount,
                retry_allowed=True,
            )

        transaction_id = str(uuid.uuid4())

        self.cart_repo.clearUserCart(request.user_id)

        self._send_payment_notification(
            user_id=request.user_id,
            amount=request.amount,
            transaction_id=transaction_id,
            success=True,
        )

        return PaymentResponse(
            status=PaymentStatus.SUCCESS,
            message="Payment successful! A confirmation has been sent to your email.",
            transaction_id=transaction_id,
            amount=request.amount,
            retry_allowed=False,
        )

    def _send_payment_notification(
        self,
        user_id: int,
        amount: float,
        transaction_id: str,
        success: bool,
    ) -> None:
        try:
            account = self.accounts_repo.get_account_info(str(user_id))
            if account is None:
                return

            notifier = Notification()
            if success:
                subject = "Payment Confirmation"
                body = (
                    f"Hello {account.username},\n\n"
                    f"Your payment of ${amount:.2f} was successful.\n"
                    f"Transaction ID: {transaction_id}\n\n"
                    "Thank you for your order!\n"
                )
            else:
                subject = "Payment Failed"
                body = (
                    f"Hello {account.username},\n\n"
                    f"Your payment of ${amount:.2f} could not be processed.\n"
                    "Please retry with a valid payment method.\n\n"
                )
            notifier.send_notification(subject, body, account.email)
        except Exception:
            pass