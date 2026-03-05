from pydantic import BaseModel

class Resturant(BaseModel):
    resturant_id: int
    name: str
    rating: float = 0
    deliveryTime: str = "0"
    deliveryDistance: str = "0"
    open: bool = False


class deliveryResturant(BaseModel):
    restaurant_id: int
    food_item: str
    delivery_time: str 
    delivery_distance: str
    customer_rating: str

