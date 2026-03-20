from pydantic import BaseModel
from typing import List

class Combo(BaseModel):
    combo_id: float
    comboItems: List[int]
    discountPrice: float
    
class Menu(BaseModel):
    menu_id: int
    items: List[int]
    menuCombos: List[Combo]


