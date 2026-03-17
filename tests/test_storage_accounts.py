from pathlib import Path

import pytest
from app.repositories.storage_accounts import AccountsStorage
from app.schemas.authenticationSchema import AccountInfo


@pytest.fixture
def storage(tmp_path: Path) -> AccountsStorage:
    return AccountsStorage(path=tmp_path / "test.json")


@pytest.fixture
def account() -> AccountInfo:
    return AccountInfo(username="alice", password="secret123", role="user", email="idan@gmail.com", token="")


def test_add_new_account_success(storage: AccountsStorage, account: AccountInfo) -> None:
    result = storage.add_new_account(account)
    assert result == account


def test_add_new_account_error(storage: AccountsStorage, account: AccountInfo) -> None:
    storage.add_new_account(account)
    with pytest.raises(ValueError):
        storage.add_new_account(account)

    pytest.raises(ValueError, match="User already exists")


def test_get_account_info(storage: AccountsStorage, account: AccountInfo) -> None:
    storage.add_new_account(account)
    info = storage.get_account_info("alice")
    assert info is not None
    assert info.username == "alice"
    assert info.password == "secret123"
    assert info.role == "user"
    assert info.email == "idan@gmail.com"
    assert info.address == ""

def test_get_nonexistent_account_info(storage: AccountsStorage) -> None:
    info = storage.get_account_info("alice")
    assert info is None

def test_get_account_role(storage: AccountsStorage, account: AccountInfo) -> None:
    storage.add_new_account(account)
    assert storage.get_account_role("alice") == "user"


def test_get_address(storage: AccountsStorage, account: AccountInfo) -> None:
    storage.add_new_account(account)
    assert storage.get_address("alice") == ""


def test_get_address_username_not_found(storage: AccountsStorage) -> None:
    assert storage.get_address("alice") is None


def test_get_address_with_address(storage: AccountsStorage) -> None:
    account_with_address = AccountInfo(username="Ethan", password="pass", role="user", email="ethan@fsfsd.com", token="", address="1267 Discovery Av. Kelowna, BC")
    storage.add_new_account(account_with_address)
    assert storage.get_address("Ethan") == "1267 Discovery Av. Kelowna, BC"
