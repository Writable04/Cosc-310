from pathlib import Path
import pytest

from app.repositories.resturant_repo import ResturantStorage
from app.schemas.resturantSchema import Resturant


@pytest.fixture
def storage(tmp_path):
    file = tmp_path / "restaurants.csv"
    return ResturantStorage(path=file)


@pytest.fixture
def sample_resturant():
    return Resturant(
        restaurant_id=1,
        name="Pizza Place",
        cuisine="Italian",
        rating="4"
    )


def test_new_resturant(storage, sample_resturant):
    result = storage.new_resturant(sample_resturant)

    assert result.restaurant_id == 1

    row = storage.find_resturant(1)
    assert row is not None
    assert row.name == "Pizza Place"


def test_find_resturant(storage, sample_resturant):
    storage.new_resturant(sample_resturant)

    found = storage.find_resturant(1)

    assert found is not None
    assert found.restaurant_id == 1
    assert found.name == "Pizza Place"


def test_update_resturant(storage, sample_resturant):
    storage.new_resturant(sample_resturant)

    updated = storage.update_resturant(1, {"name": "Better Pizza"})

    assert updated is not None
    assert updated.name == "Better Pizza"

    row = storage.find_resturant(1)
    assert row.name == "Better Pizza"


def test_remove_resturant(storage, sample_resturant):
    storage.new_resturant(sample_resturant)

    removed = storage.remove_resturant(1)

    assert removed is not None
    assert removed.restaurant_id == 1

    row = storage.find_resturant(1)
    assert row is None