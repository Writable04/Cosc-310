from pathlib import Path
from app.schemas.menuSchema import Menu
from app.repositories.storage_base_csv import CSVStorage

class MenuStorage:
    def __init__(self, path: Path | None = None):
        path = path or Path(__file__).parent / "menus.csv"
        fields = list(Menu.model_fields.keys())
        self.storage = CSVStorage(path, fields)
    
    def new_Menu(self, menu: Menu):
        self.storage.write_row(menu.dict())
        return menu

    def find_menu(self, menu_id: int):
        row = self.storage.find_by("menu_id", str(menu_id))
        if row:
            return Menu(**row)
        return None

    def update_menu(self, menu_id: int, updated_data: dict):
        self.storage.update("menu_id", str(menu_id), updated_data)
        row = self.storage.find_by("menu_id", str(menu_id))
        if row:
            return Menu(**row)
        return None