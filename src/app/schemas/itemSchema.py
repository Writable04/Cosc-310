from pydantic import BaseModel

class Item(BaseModel):
    item_id: int
    name: str
    price: str
    menu_id: int