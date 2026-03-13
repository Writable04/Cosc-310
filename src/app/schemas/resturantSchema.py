from pydantic import BaseModel

class Resturant(BaseModel):
    restaurant_id: int
    name: str
    cusine: str
    rating: float = 0
    deliveryDistance: str = "0"
    

