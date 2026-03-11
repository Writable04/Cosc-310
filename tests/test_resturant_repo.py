import pytest
from pathlib import Path
from app.repositories.resturant_repo import ResturantStorage
from app.schemas.resturantSchema import Resturant


@pytest.fixture
def storage(tmp_path):
    test_file = tmp_path / "restaurants.csv"
    storage = ResturantStorage(path=test_file)
    return storage

@pytest.fixture
def sample_restaurant():
    return Resturant.model_construct(
        restaurant_id=1,
        name="Bobs burgers",
        raiting="4",
        cuisine="Italian"
    )

def test_new_resturant(storage, sample_restaurant):
    storage.new_resturant(sample_restaurant)

    rows = storage.read_all()

    assert len(rows) == 1
    assert rows[0]["restaurant_id"] == "1"
    assert rows[0]["name"] == "Bobs burgers"


def test_find_resturant(storage, sample_restaurant):
    storage.new_resturant(sample_restaurant)

    result = storage.find_resturant(1)

    assert result is not None
    assert result.restaurant_id == 1
    assert result.name == "Bobs burgers"


def test_update_resturant(storage, sample_restaurant):
    storage.new_resturant(sample_restaurant)

    updated = storage.update_resturant(1, {"name": "bobs better burgers"})

    assert updated is not None
    assert updated.name == "bobs better burgers"

    result = storage.find_resturant(1)
    assert result.name == "bobs better burgers"


def test_remove_resturant(storage, sample_restaurant):
    storage.new_resturant(sample_restaurant)

    removed = storage.remove_resturant(1)

    assert removed is not None
    assert removed.restaurant_id == 1

    result = storage.find_resturant(1)
    assert result is None