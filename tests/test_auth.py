import pytest
from unittest.mock import MagicMock

from app.services.authentication.auth import Authentication
from app.schemas.authenticationSchema import AccountInfo

@pytest.fixture
def mock_storage() -> MagicMock:
    return MagicMock()


@pytest.fixture
def auth(mock_storage: MagicMock) -> Authentication:
    return Authentication(mock_storage)


def test_encrypt_password(auth: Authentication) -> None:
    result = auth.encrypt_password("ValidPass123")
    assert auth.encryption.verify("ValidPass123", result)
    assert result != "ValidPass123"


def test_verify_password_valid(auth: Authentication, mock_storage: MagicMock) -> None:
    encrypted_password = auth.encryption.hash("Password1")
    mock_storage.get_account_info.return_value = AccountInfo(
        username="John", password=encrypted_password, role="admin", email="idan@gmail.com", token=""
    )

    assert auth.verify_password("Password1", encrypted_password) is True


def test_verify_password_invalid(auth: Authentication, mock_storage: MagicMock) -> None:
    encrypted_password = auth.encryption.hash("Password1")
    mock_storage.get_account_info.return_value = AccountInfo(
        username="John", password=encrypted_password, role="admin", email="idan@gmail.com", token=""
    )

    assert auth.verify_password("OtherPassword", encrypted_password) is False


def test_is_token_valid_when_account_missing(auth: Authentication, mock_storage: MagicMock) -> None:
    mock_storage.get_account_info.return_value = None
    assert auth._is_token_valid("idannn", "token") is False


def test_is_token_valid_true(auth: Authentication, mock_storage: MagicMock) -> None:
    mock_storage.get_account_info.return_value = AccountInfo(
        username="Idannnnn", password="password123", role="admin", token="correct", email="idan@gmail.com"
    )
    assert auth._is_token_valid("John", "wrong") is False


def test_is_token_valid_false(auth: Authentication, mock_storage: MagicMock) -> None:
    mock_storage.get_account_info.return_value = AccountInfo(
        username="Idan", password="password123", role="admin", token="correct", email="idan@gmail.com"
    )
    assert auth._is_token_valid("John", "correct") is True
