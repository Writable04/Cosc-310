from pydantic import BaseModel

class Resturant(BaseModel):
    resturant_id: int
    name: str
    rating: float = 0
    deliveryTime: str = "0"
    deliveryDistance: str = "0"
    open: bool = False

