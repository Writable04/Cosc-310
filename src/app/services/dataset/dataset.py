from pathlib import Path
from app.repositories.storage_base_csv import CSVStorage

def getItemList() -> None:
    DATA_DIR = Path(__file__).parent.parent.parent / "data" / "resturantData"
    path = DATA_DIR / "food_delivery.csv"
    storage = CSVStorage(path, [])
    rows = storage.read_all()
    menu_items = [row["food_item"] for row in rows]
    menu_items = list(set(menu_items))
    putPath = DATA_DIR / "items.csv"
    writeStorage = CSVStorage(putPath, ["Items"])
    
    for item in menu_items:
        writeStorage.write_row({"Items": item})
