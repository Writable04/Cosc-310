from pydantic import BaseModel
from typing import List

class Combo (BaseModel):
    combo_id: int
    comboItems: List[int]
    discountPrice: float
    menu_id: int
    
class Menu(BaseModel):
    menu_id: int
    items: List[int]
    menuCombos: List[Combo]


