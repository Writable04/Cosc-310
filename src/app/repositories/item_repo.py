from pathlib import Path
from app.schemas.itemSchema import Item
from app.repositories.storage_base_csv import CSVStorage

class ItemStorage(CSVStorage):
    def __init__(self, path: Path | None = None):
        path = path or Path(__file__).parent.parent / "data/resturantData/items.csv"
        fields = list(Item.model_fields.keys())
        super().__init__(path,fields)
    
    def new_item(self, item: Item):
        self.write_row(item.dict())
        return item

    def find_item(self, item_id: int):
        row = self.find_by("item_id", str(item_id))
        if row:
            return Item(**row)
        return None

    def update_item(self, item_id: int, updated_data: dict):
        self.update("item_id", str(item_id), updated_data)
        row = self.find_by("item_id", str(item_id))
        if row:
            return Item(**row)
        return None

    def remove_item(self, item_id: int):
            row = self.find_by("item_id", str(item_id))
            if not row:
                return None
            self.delete("item_id", str(item_id))
            return Item(**row)