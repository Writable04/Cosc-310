import pytest
from pathlib import Path

from app.repositories.menu_repo import MenuStorage
from app.schemas.menuSchema import Menu


@pytest.fixture
def storage(tmp_path):
    file = tmp_path / "menus.csv"
    return MenuStorage(path=file)


@pytest.fixture
def sample_menu():
    return Menu(
        menu_id=1,
        itemList="burger, hotdogs"
    )


def test_new_menu(storage, sample_menu):
    menu = storage.new_Menu(sample_menu)

    assert menu.menu_id == 1

    row = storage.find_menu(1)
    assert row is not None
    assert row.itemList == "burger, hotdogs"


def test_find_menu(storage, sample_menu):
    storage.new_Menu(sample_menu)

    result = storage.find_menu(1)

    assert result is not None
    assert result.menu_id == 1
    assert result.restaurant_id == 10


def test_update_menu(storage, sample_menu):
    storage.new_Menu(sample_menu)

    updated = storage.update_menu(1, {"itemList": "burger, taco"})

    assert updated is not None
    assert updated.name == "burger, taco"

    row = storage.find_menu(1)
    assert row.name == "burger, taco"


def test_remove_menu(storage, sample_menu):
    storage.new_Menu(sample_menu)

    removed = storage.remove_menu(1)

    assert removed is not None
    assert removed.menu_id == 1

    row = storage.find_menu(1)
    assert row is None