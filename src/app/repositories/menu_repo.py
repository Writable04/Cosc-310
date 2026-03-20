from pathlib import Path
from typing import List
import ast
from app.schemas.menuSchema import Menu
from app.repositories.storage_base import Storage

class MenuStorage(Storage[dict]):
    def __init__(self, path: Path | None = None):
        path = path or Path(__file__).parent.parent / "data/resturantData/menus.json"
        super().__init__(path)

    def new_menu(self, menu: Menu) -> Menu:
        data = self._load()

        if menu.menu_id == 0:
            next_id = max([int(k) for k in data.keys()], default=0) + 1
            menu.menu_id = next_id

        self.write(str(menu.menu_id), menu.model_dump())
        return menu

    def find_menu(self, menu_id: int) -> Menu | None:
        data = self.read(str(menu_id))
        if data:
            return Menu(**data)
        return None

    def get_all_menus(self) -> List[Menu]:
        data = self._load()
        return [Menu(**menu) for menu in data.values()]

    def update_menu(self, menu_id: int, updates: dict) -> Menu:
        self.update(str(menu_id), updates)
        updated = self.read(str(menu_id))
        return Menu(**updated)

    def remove_menu(self, menu_id: int) -> None:
        data = self._load()
        if str(menu_id) in data:
            del data[str(menu_id)]
            self._save(data)
        else:
            raise ValueError("Menu not found")