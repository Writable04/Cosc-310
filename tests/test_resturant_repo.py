import pytest
from pathlib import Path
from app.repositories.resturant_repo import ResturantStorage
import app.repositories.resturant_repo as resturant_repo
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
        cusine="Italian",
        rating="4",
        restaurantAddress="123 Main St, Kelowna, BC"
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


def test_get_restaurant_address(storage, sample_restaurant):
    storage.new_resturant(sample_restaurant)

    address = storage.get_restaurant_address(1)

    assert address == "123 Main St, Kelowna, BC"


def test_get_restaurant_distances(storage, sample_restaurant, monkeypatch):
    storage.new_resturant(sample_restaurant)

    monkeypatch.setattr(resturant_repo.map_api, "calculateDeliveryDistanceKM", lambda *_: 12.34)
    monkeypatch.setattr(resturant_repo.map_api, "calculateDeliveryTimeMins", lambda *_: 56)

    dist, duration = storage.get_restaurant_distances(1, "456 Dilworth Dr, Kelowna, BC")
    assert dist == 12.34
    assert duration == 56


def test_get_resturants_with_distances(storage, monkeypatch):
    storage.new_resturant(
        Resturant(
            restaurant_id=1,
            name="Burgers",
            cuisine="American",
            rating=4.5,
            restaurantAddress="123 Main St, Kelowna, BC",
        )
    )
    storage.new_resturant(
        Resturant(
            restaurant_id=2,
            name="Tacos",
            cuisine="Mexican",
            rating=4.9,
            restaurantAddress="456 Discovery Ave, Kelowna, BC",
        )
    )

    monkeypatch.setattr(
        storage,
        "get_restaurant_distances",
        lambda restaurant_id, _user_address: (5, 10),
    )

    results = storage.get_resturants_with_distances("2423 Dilworth Dr, Kelowna, BC")

    assert len(results) == 2
    assert all(isinstance(result, Resturant) for result in results)
    assert results[0].distanceKM == 5
    assert results[0].durationMinutes == 10
    assert results[1].distanceKM == 5
    assert results[1].durationMinutes == 10
