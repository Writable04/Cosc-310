import pytest
from unittest.mock import MagicMock

from app.authentication.auth import Authentication
from app.schemas.authenticationSchema import AccountInfo

@pytest.fixture
def mock_storage() -> MagicMock:
    return MagicMock()


@pytest.fixture
def auth(mock_storage: MagicMock) -> Authentication:
    return Authentication(mock_storage)


def test_check_and_encrypt_password_valid(auth: Authentication) -> None:
    result = auth.check_and_encrypt_password("ValidPass123")
    assert auth.encryption.verify("ValidPass123", result)
    assert result != "ValidPass123"


def test_check_and_encrypt_password_too_short(auth: Authentication) -> None:
    with pytest.raises(ValueError, match="Password is not valid"):
        auth.check_and_encrypt_password("idan")


def test_check_and_encrypt_password_no_uppercase(auth: Authentication) -> None:
    with pytest.raises(ValueError, match="Password is not valid"):
        auth.check_and_encrypt_password("blablablabadsf")


def test_check_and_encrypt_password_no_number(auth: Authentication) -> None:
    with pytest.raises(ValueError, match="Password is not valid"):
        auth.check_and_encrypt_password("IdanBlananana")


def test_verify_password_valid(auth: Authentication, mock_storage: MagicMock) -> None:
    encrypted_password = auth.encryption.hash("Password1")
    mock_storage.get_account_info.return_value = AccountInfo(
        username="John", password=encrypted_password, role="admin"
    )

    assert auth.verify_password("John", "Password1") is True


def test_verify_password_invalid(auth: Authentication, mock_storage: MagicMock) -> None:
    encrypted_password = auth.encryption.hash("Password1")
    mock_storage.get_account_info.return_value = AccountInfo(
        username="John", password=encrypted_password, role="admin"
    )

    assert auth.verify_password("John", "OtherPassword") is False
