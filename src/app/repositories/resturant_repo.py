from pathlib import Path
from app.schemas.resturantSchema import Resturant, deliveryResturant
from app.repositories.storage_base_csv import CSVStorage

class ResturantStorage(CSVstorage):
    def __init__(self, path: Path | None = None):
        path = path or Path(__file__).parent / "restaurants.csv"
        fields = list(Resturant.model_fields.keys())
        super().__init__(pat,fields)

    def new_resturant(self, resturant: Resturant):
        self.storage.write_row(resturant.dict())
        return resturant

    def find_resturant(self, restaurant_id: int):
        row = self.storage.find_by("restaurant_id", str(restaurant_id))
        if row:
            return Resturant(**row)
        return None

    def update_resturant(self, restaurant_id: int, updated_data: dict):
        self.storage.update("restaurant_id", str(restaurant_id), updated_data)
        row = self.storage.find_by("restaurant_id", str(restaurant_id))
        if row:
            return Resturant(**row)
        return None