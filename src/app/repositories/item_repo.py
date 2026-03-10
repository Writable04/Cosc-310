from pathlib import Path
from app.schemas.itemSchema import Item
from app.repositories.storage_base_csv import CSVStorage

class ItemStorage:
    def __init__(self, path: Path | None = None):
        path = path or Path(__file__).parent / "items.csv"
        fields = list(Item.model_fields.keys())
        self.storage = CSVStorage(path, fields)
    
    def new_item(self, item: Item):
        self.storage.write_row(item.dict())
        return item

    def find_item(self, item_id: int):
        row = self.storage.find_by("item_id", str(item_id))
        if row:
            return Item(**row)
        return None

    def update_item(self, item_id: int, updated_data: dict):
        self.storage.update("item_id", str(item_id), updated_data)
        row = self.storage.find_by("item_id", str(item_id))
        if row:
            return Item(**row)
        return None