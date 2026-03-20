from pathlib import Path
from app.repositories.storage_base_csv import CSVStorage

def assign_restaurant_id(restaurant, resturant_storage):
    if restaurant.restaurant_id == 0:
        data = resturant_storage.read_all()

        if not data:
            restaurant.restaurant_id = 1
        else:
            max_id = max(int(r["restaurant_id"]) for r in data)
            restaurant.restaurant_id = max_id + 1

    return restaurant
