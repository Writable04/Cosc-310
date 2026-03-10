import pytest
from pathlib import Path

from app.repositories.item_repo import ItemStorage
from app.schemas.itemSchema import Item


@pytest.fixture
def storage(tmp_path):
    """Temporary CSV storage for tests."""
    file = tmp_path / "items.csv"
    return ItemStorage(path=file)


@pytest.fixture
def sample_item():
    return Item(
        item_id=1,
        name="Burger",
        price=9.99,
        menu_id=5
    )


def test_new_item(storage, sample_item):
    item = storage.new_item(sample_item)

    assert item.item_id == 1

    row = storage.find_item(1)
    assert row is not None
    assert row.name == "Burger"


def test_find_item(storage, sample_item):
    storage.new_item(sample_item)

    result = storage.find_item(1)

    assert result is not None
    assert result.item_id == 1
    assert result.name == "Burger"


def test_update_item(storage, sample_item):
    storage.new_item(sample_item)

    updated = storage.update_item(1, {"name": "Cheeseburger"})

    assert updated is not None
    assert updated.name == "Cheeseburger"

    row = storage.find_item(1)
    assert row.name == "Cheeseburger"


def test_remove_item(storage, sample_item):
    storage.new_item(sample_item)

    removed = storage.remove_item(1)

    assert removed is not None
    assert removed.item_id == 1

    row = storage.find_item(1)
    assert row is None