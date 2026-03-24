from pydantic import BaseModel
from app.schemas.menuSchema import Combo

class CartItem(BaseModel):
    name: str
    itemID: int
    quantity: int
    price: float

class AppliedCombos(BaseModel): 
    combo_id: int
    comboItems: list[int]
    discountPrice: float 
    quantity: int 

class Cart(BaseModel):
    user_id: int
    restaurant: str
    items: list[CartItem] = []
    subtotal: float = 0.0
    appliedCombos: list[AppliedCombos] = []
    totalDiscount: float = 0.0
    checkout_total: float = 0.0
    
