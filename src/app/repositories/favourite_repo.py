from enum import Enum
from pathlib import Path

from app.repositories.item_repo import ItemStorage
from app.repositories.resturant_repo import ResturantStorage
from app.repositories.storage_base import Storage
from app.schemas.favouriteSchema import UserFavourites

class FavouriteType(Enum):
    RESTAURANT = "restaurant"
    ITEM = "item"

class Favourite:
    def __init__(self, username: str, id: int, type: FavouriteType, resturant_storage: ResturantStorage, item_storage: ItemStorage):
        self.username = username
        self.id = id
        self.type = type
        self.restaurants = resturant_storage
        self.items = item_storage

    def get(self) -> dict:
        if self.type == FavouriteType.RESTAURANT:
            return self.restaurants.find_resturant(self.id)
        elif self.type == FavouriteType.ITEM:
            return self.items.find_item(self.id)
        else:
            return None

class FavouriteStorage(Storage[UserFavourites]):
    def __init__(self, resturant_storage: ResturantStorage, item_storage: ItemStorage, path: Path | None = None) -> None:
        path = path or Path(__file__).parent.parent / "data" / "favourites.json"
        super().__init__(path)
        self.restaurants = resturant_storage
        self.items = item_storage

    def get_favourites_full_data(self, username: str) -> dict:
        favourites = self.get_favourites(username)
        favourites_data = favourites.model_dump(mode="json")
        favourites_data["restaurant_ids"] = [self.restaurants.find_resturant(restaurant_id) for restaurant_id in favourites.restaurant_ids]
        favourites_data["item_ids"] = [self.items.find_item(item_id) for item_id in favourites.item_ids]
        return favourites_data

    def get_favourites(self, username: str) -> UserFavourites:
        data = self.read(username)
        if data is None:
            new_favourites = UserFavourites()
            self.write(username, new_favourites.model_dump(mode="json"))
            return new_favourites

        return UserFavourites(**data)

    def add_favourite(self, username: str, id: int, type: FavouriteType) -> UserFavourites | None:
        favourite = Favourite(username, id, type, self.restaurants, self.items)
        favourite_data = favourite.get()
        if favourite_data is None:
            return None

        favourites = self.get_favourites(username)

        if type == FavouriteType.RESTAURANT:
            favourites = self._add_restaurant(favourites, id)
        elif type == FavouriteType.ITEM:
            favourites = self._add_item(favourites, id)
        else:
            return None

        self.write(username, favourites.model_dump(mode="json"))
        return favourites

    def remove_favourite(self, username: str, id: int, type: FavouriteType) -> UserFavourites | None:
        favourite = Favourite(username, id, type, self.restaurants, self.items)
        favourite_data = favourite.get()
        if favourite_data is None:
            return None

        favourites = self.get_favourites(username)

        if type == FavouriteType.RESTAURANT:
            favourites = self._remove_restaurant(favourites, id)
        elif type == FavouriteType.ITEM:
            favourites = self._remove_item(favourites, id)
        else:
            return None

        self.write(username, favourites.model_dump(mode="json"))
        return favourites

    def _add_restaurant(self, favourites: UserFavourites, restaurant_id: int) -> UserFavourites:
        if restaurant_id in favourites.restaurant_ids:
            return favourites

        restaurant_ids = favourites.restaurant_ids
        restaurant_ids.append(restaurant_id)
        restaurant_ids.sort()
        return UserFavourites(restaurant_ids=restaurant_ids, item_ids=favourites.item_ids)

    def _add_item(self, favourites: UserFavourites, item_id: int) -> UserFavourites:
        if item_id in favourites.item_ids:
            return favourites
            
        item_ids = favourites.item_ids
        item_ids.append(item_id)
        item_ids.sort()
        return UserFavourites(restaurant_ids=favourites.restaurant_ids, item_ids=item_ids)

    def _remove_restaurant(self, favourites: UserFavourites, restaurant_id: int) -> UserFavourites:
        restaurant_ids = favourites.restaurant_ids
        if restaurant_id in restaurant_ids:
            restaurant_ids.remove(restaurant_id)
        return UserFavourites(restaurant_ids=restaurant_ids, item_ids=favourites.item_ids)

    def _remove_item(self, favourites: UserFavourites, item_id: int) -> UserFavourites:
        item_ids = favourites.item_ids
        if item_id in item_ids:
            item_ids.remove(item_id)
        return UserFavourites(restaurant_ids=favourites.restaurant_ids, item_ids=item_ids)