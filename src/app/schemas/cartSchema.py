from pydantic import BaseModel

class CartItem(BaseModel):
    name: str
    itemID: int
    quantity: int
    price: float

class Cart(BaseModel):
    user_id: int
    restaurant: str
    items: list[CartItem] = []
    subtotal: float