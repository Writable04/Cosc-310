from pathlib import Path
from app.schemas.resturantSchema import Resturant
from app.repositories.storage_base_csv import CSVStorage

class ResturantStorage(CSVStorage):
    def __init__(self, path: Path | None = None):
        path = path or Path(__file__).parent.parent / "data/resturantData/restaurants.csv"
        fields = list(Resturant.model_fields.keys())
        super().__init__(path,fields)

    def new_resturant(self, resturant: Resturant):
        self.write_row(resturant.dict())
        return resturant

    def find_resturant(self, restaurant_id: int):
        row = self.find_by("restaurant_id", str(restaurant_id))
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