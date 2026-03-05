import pytest
from unittest.mock import MagicMock

from app.authentication.auth import Authentication
from app.authentication.registration import Registration
from app.db.storage_accounts import AccountsStorage
from app.models import AccountInfo

@pytest.fixture
def mock_storage() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_auth() -> MagicMock:
    return MagicMock()


@pytest.fixture
def registration(mock_storage: AccountsStorage, mock_auth: Authentication) -> Registration:
    return Registration(mock_storage, mock_auth)


def test_register_success(registration: Registration, mock_storage: AccountsStorage, mock_auth: Authentication) -> None:
    account = AccountInfo(username="idan", password="Idannnnnnn123", role="admin", token="test-token")

    # First call: user does not exist; second call: from login() after add_new_account
    mock_storage.get_account_info.side_effect = [None, account]
    mock_storage.add_new_account.return_value = account
    mock_auth.encrypt_password.return_value = account.password
    mock_auth.generate_new_token.return_value = "test-token"
    mock_auth.verify_password.return_value = True

    assert registration.register(account.username, account.password, account.password, account.role) == "test-token"


def test_register_account_already_exists(registration: Registration, mock_storage: AccountsStorage, mock_auth: Authentication) -> None:
    account = AccountInfo(username="idan", password="Idannnnnnn123", role="admin", token="test-token")

    mock_storage.get_account_info.return_value = account
    mock_storage.add_new_account.return_value = account
    mock_auth.encrypt_password.return_value = account.password

    with pytest.raises(ValueError, match="Username already exists"):
        registration.register(account.username, account.password, account.password, account.role)


def test_register_account_password_does_not_match(registration: Registration, mock_storage: AccountsStorage, mock_auth: Authentication) -> None:
    account = AccountInfo(username="idan", password="Idannnnnnn123", role="admin", token="test-token")

    mock_storage.get_account_info.return_value = None
    mock_auth.encrypt_password.return_value = account.password

    with pytest.raises(ValueError, match="Passwords do not match"):
        registration.register(account.username, account.password, "Idannnnnnn1234", account.role)


def test_register_account_password_is_not_valid(registration: Registration, mock_storage: AccountsStorage, mock_auth: Authentication) -> None:
    account = AccountInfo(username="idan", password="Idannnn", role="admin", token="test-token")

    mock_storage.get_account_info.return_value = None
    mock_auth.encrypt_password.return_value = account.password

    with pytest.raises(ValueError, match="Password is not valid"):
        registration.register(account.username, account.password, account.password, account.role)


def test_password_validation_too_short(registration: Registration) -> None:
    assert registration._is_password_valid("idan") is False


def test_password_validation_no_uppercase(registration: Registration) -> None:
    assert registration._is_password_valid("idanidanidan") is False


def test_password_validation_no_number(registration: Registration) -> None:
    assert registration._is_password_valid("Idanidanidan") is False


def test_password_validation_valid(registration: Registration) -> None:
    assert registration._is_password_valid("Idan12345678") is True
