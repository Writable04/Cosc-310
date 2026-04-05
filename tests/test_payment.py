import pytest
from unittest.mock import MagicMock
from pathlib import Path

from app.services.payment.payment import PaymentService, _validate_payment_method, _is_expired
from app.repositories.payment_repo import PaymentMethodStorage
from app.schemas.paymentSchema import PaymentMethod, PaymentRequest, SavedPaymentMethod, PaymentStatus

@pytest.fixture
def card() -> PaymentMethod:
    return PaymentMethod(
        card_holder_name="Idan Lisman",
        card_number="4111111111111111",
        expiry_month=12,
        expiry_year=2099,
        cvv="123",
        card_type="credit",
    )

@pytest.fixture
def saved() -> SavedPaymentMethod:
    return SavedPaymentMethod(
        method_id="m-1", card_holder_name="Idan Lisman",
        last_four="1111", expiry_month=12, expiry_year=2099, card_type="credit",
    )

@pytest.fixture
def payment_repo(tmp_path: Path) -> PaymentMethodStorage:
    return PaymentMethodStorage(path=tmp_path / "payments.json")

@pytest.fixture
def svc() -> PaymentService:
    service = PaymentService.__new__(PaymentService)
    service.payment_repo = MagicMock()
    service.cart_repo = MagicMock()
    service.accounts_repo = MagicMock()
    return service


def test_valid_card_passes(card):
    assert _validate_payment_method(card) == (True, "OK")

def test_declined_card(card):
    card.card_number = "4111000000000000"
    assert _validate_payment_method(card)[0] is False

def test_expired_card(card):
    card.expiry_year = 2000
    assert _validate_payment_method(card)[0] is False

def test_bad_cvv(card):
    card.cvv = "000"
    assert _validate_payment_method(card)[0] is False

def test_short_card_number(card):
    card.card_number = "4111"
    assert _validate_payment_method(card)[0] is False

def test_is_expired():
    assert _is_expired(1, 2000) is True
    assert _is_expired(12, 2099) is False

def test_save_and_get(payment_repo, saved):
    payment_repo.save_method("testuser", saved)
    assert payment_repo.get_method("testuser", saved.method_id).last_four == "1111"

def test_first_card_is_default(payment_repo, saved):
    payment_repo.save_method("testuser", saved)
    assert payment_repo.get_default_method("testuser").method_id == saved.method_id

def test_delete_method(payment_repo, saved):
    payment_repo.save_method("testuser", saved)
    assert payment_repo.delete_method("testuser", saved.method_id) is True
    assert payment_repo.get_method("testuser", saved.method_id) is None

def test_delete_nonexistent(payment_repo):
    assert payment_repo.delete_method("testuser", "bad-id") is False

def test_successful_payment(svc, card):
    result = svc.process_payment(PaymentRequest(username="testuser", restaurant="Bobs Burgers", amount=49.99, new_method=card))
    assert result.status == PaymentStatus.SUCCESS
    assert result.retry_allowed is False

def test_success_clears_cart(svc, card):
    svc.process_payment(PaymentRequest(username="testuser", restaurant="Bobs Burgers", amount=49.99, new_method=card))
    svc.cart_repo.clearUserCart.assert_called_once_with("testuser")  # now str not int

def test_zero_amount_fails(svc, card):
    result = svc.process_payment(PaymentRequest(username="testuser", restaurant="Bobs Burgers", amount=0.0, new_method=card))
    assert result.status == PaymentStatus.FAILED
    assert result.retry_allowed is True

def test_declined_card_retry(svc, card):
    card.card_number = "4111000000000000"
    result = svc.process_payment(PaymentRequest(username="testuser", restaurant="Bobs Burgers", amount=49.99, new_method=card))
    assert result.status == PaymentStatus.FAILED
    assert result.retry_allowed is True

def test_no_method_fails(svc):
    svc.payment_repo.get_default_method.return_value = None
    result = svc.process_payment(PaymentRequest(username="testuser", restaurant="Bobs Burgers", amount=49.99))
    assert result.status == PaymentStatus.FAILED
    assert result.retry_allowed is True