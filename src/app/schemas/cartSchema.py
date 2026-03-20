from pydantic import BaseModel
from app.schemas.menuSchema import Combo

class CartItem(BaseModel):
    name: str
    itemID: int
    quantity: int
    price: float

class AppliedCombos(BaseModel): 
    combo_id: float
    comboItems: list[int]
    discountPrice: float 
    count: int 

class Cart(BaseModel):
    user_id: int
    restaurant: str
    items: list[CartItem] = []
    subtotal: float = 0.0
    appliedCombos: list[AppliedCombos] = []
    totalDiscount: float = 0.0
    final_total: float = 0.0
    
