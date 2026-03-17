from pydantic import BaseModel
from typing import List

class Menu(BaseModel):
    menu_id: int
    items: List[int] = []