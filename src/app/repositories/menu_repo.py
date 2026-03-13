from pathlib import Path
import ast
from app.schemas.menuSchema import Menu
from app.repositories.storage_base_csv import CSVStorage

class MenuStorage(CSVStorage):
    def __init__(self, path: Path | None = None):
        path = path or Path(__file__).parent.parent / "data/resturantData/menus.csv"
        fields = list(Menu.model_fields.keys())
        super().__init__(path,fields)
    
    def new_Menu(self, menu: Menu):
        self.write_row(menu.model_dump())
        return menu

    def find_menu(self, menu_id: int):
        row = self.find_by("menu_id", str(menu_id))
        if row:
            if isinstance(row["items"], str):
                row["items"] = ast.literal_eval(row["items"])
            return Menu(**row)
        return None

    def update_menu(self, menu_id: int, updated_data: dict):
        self.update("menu_id", str(menu_id), updated_data)
        row = self.find_by("menu_id", str(menu_id))
        if row:
            if isinstance(row["items"], str):
                row["items"] = ast.literal_eval(row["items"])
            return Menu(**row)
        return None

    def remove_menu(self, menu_id: int):
        row = self.find_by("menu_id", str(menu_id))
        if not row:
            return None
        self.delete("menu_id", str(menu_id))
        if isinstance(row["items"], str):
            row["items"] = ast.literal_eval(row["items"])
        return Menu(**row)