from unittest.mock import MagicMock

import pytest

from app.repositories.favourite_repo import FavouriteStorage, FavouriteType
from app.schemas.favouriteSchema import UserFavourites
from app.schemas.itemSchema import Item
from app.schemas.resturantSchema import Resturant


def _stub_restaurant(restaurant_id: int) -> Resturant:
    return Resturant(
        restaurant_id=restaurant_id,
        name="Test",
        cuisine="Test",
        restaurantAddress="Test",
    )


def _stub_item(item_id: int) -> Item:
    return Item(item_id=item_id, name="Test", price="10", menu_id=0)


@pytest.fixture
def mock_restaurants() -> MagicMock:
    mock_restaurants = MagicMock()
    mock_restaurants.find_resturant.side_effect = (
        lambda restaurant_id: _stub_restaurant(restaurant_id) if restaurant_id in (1, 2) else None
    )
    return mock_restaurants


@pytest.fixture
def mock_items() -> MagicMock:
    mock_items = MagicMock()
    mock_items.find_item.side_effect = lambda item_id: _stub_item(item_id) if item_id in (10, 20) else None
    return mock_items


@pytest.fixture
def storage(tmp_path, mock_restaurants: MagicMock, mock_items: MagicMock) -> FavouriteStorage:
    return FavouriteStorage(mock_restaurants, mock_items, path=tmp_path / "favourites.json")


def test_get_favourites_empty(storage: FavouriteStorage) -> None:
    username = "Idannn"
    favourites = storage.get_favourites(username)
    assert favourites == UserFavourites()


def test_add_restaurants(storage: FavouriteStorage) -> None:
    username = "Idannn"
    assert storage.add_favourite(username, 2, FavouriteType.RESTAURANT) == UserFavourites(restaurant_ids=[2], item_ids=[])
    assert storage.add_favourite(username, 1, FavouriteType.RESTAURANT) == UserFavourites(restaurant_ids=[1, 2], item_ids=[])

def test_add_restaurants_duplicate(storage: FavouriteStorage) -> None:
    username = "Idannn"
    assert storage.add_favourite(username, 2, FavouriteType.RESTAURANT) == UserFavourites(restaurant_ids=[2], item_ids=[])
    assert storage.add_favourite(username, 2, FavouriteType.RESTAURANT) == UserFavourites(restaurant_ids=[2], item_ids=[])


def test_add_restaurant_unknown(storage: FavouriteStorage) -> None:
    username = "Idannn"
    assert storage.add_favourite(username, 100, FavouriteType.RESTAURANT) is None


def test_remove_restaurant(storage: FavouriteStorage) -> None:
    username = "Idannn"
    storage.add_favourite(username, 1, FavouriteType.RESTAURANT)
    assert storage.remove_favourite(username, 1, FavouriteType.RESTAURANT) == UserFavourites()
    assert storage.get_favourites(username) == UserFavourites()
    assert storage.remove_favourite(username, 1, FavouriteType.RESTAURANT) == UserFavourites()

    
def test_add_items(storage: FavouriteStorage) -> None:
    username = "Idannn"
    assert storage.add_favourite(username, 20, FavouriteType.ITEM) == UserFavourites(restaurant_ids=[], item_ids=[20])
    assert storage.add_favourite(username, 10, FavouriteType.ITEM) == UserFavourites(restaurant_ids=[], item_ids=[10, 20])

def test_add_item_unknown(storage: FavouriteStorage) -> None:
    username = "Idannn"
    assert storage.add_favourite(username, 100, FavouriteType.ITEM) is None


def test_remove_item(storage: FavouriteStorage) -> None:
    username = "Idannn"
    storage.add_favourite(username, 10, FavouriteType.ITEM)
    assert storage.remove_favourite(username, 10, FavouriteType.ITEM) == UserFavourites()
    assert storage.remove_favourite(username, 10, FavouriteType.ITEM) == UserFavourites()
