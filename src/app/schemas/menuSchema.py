from pydantic import BaseModel
from typing import List

class Menu(BaseModel):
    resturant_id: int
    items: List[str] = []