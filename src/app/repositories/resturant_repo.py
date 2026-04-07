import json
from pathlib import Path
from typing import Any

from app.schemas.resturantSchema import Resturant
from app.repositories.storage_base_csv import CSVStorage

from app.repositories.map_storage import MapStorage

map_api = MapStorage()

class ResturantStorage(CSVStorage):
    def __init__(self, path: Path | None = None):
        path = path or Path(__file__).parent.parent / "data/resturantData/restaurants.csv"
        fields = list(Resturant.model_fields.keys())
        super().__init__(path,fields)

    def new_resturant(self, resturant: Resturant):
        self.write_row(resturant.dict())
        return resturant

    def find_resturant(self, restaurant_id: int, user_address: str = None) -> Resturant:
        row = self.find_by("restaurant_id", str(restaurant_id))
        if row:
            if user_address is not None:
                dist, duration = self.get_restaurant_distances(restaurant_id, user_address)
                row["durationMinutes"] = duration
                row["distanceKM"] = dist

            return Resturant(**row)
        return None

    def find_resturant_query(self, entry: str,query: str):
        row = self.find_by(query, str(entry))
        if row:
            return Resturant(**row)
        return None

    def update_resturant(self, restaurant_id: int, updated_data: dict):
        self.update("restaurant_id", str(restaurant_id), updated_data)
        row = self.find_by("restaurant_id", str(restaurant_id))
        if row:
            return Resturant(**row)
        return None
    
    def remove_resturant(self, restaurant_id: int):
        row = self.find_by("restaurant_id", str(restaurant_id))
        if not row:
            return None
        self.delete("restaurant_id", str(restaurant_id))
        return Resturant(**row)

    def get_resturants_with_distances(self, user_address: str) -> list[dict[str, Any]]:
        rows_out: list[dict[str, Any]] = []
        for row in self.read_all():
            row = dict(row)
            rid = int(row["restaurant_id"])
            dist, duration = self.get_restaurant_distances(rid, user_address)
            row["durationMinutes"] = duration
            row["distanceKM"] = dist
            rows_out.append(row)
        return rows_out

    def get_restaurant_address(self, restaurant_id: int) -> str | None:
        restaurant = self.find_resturant(restaurant_id)
        if restaurant is not None:
            return restaurant.restaurantAddress

        return None

    def get_restaurant_distances(self, restaurant_id: int, user_address: str) -> tuple[float, int]:
        restaurant_address = self.get_restaurant_address(restaurant_id)
        if restaurant_address is not None and restaurant_address != "":
            dist = map_api.calculateDeliveryDistanceKM(user_address, restaurant_address)
            duration = map_api.calculateDeliveryTimeMins(user_address, restaurant_address)
            return dist, duration
