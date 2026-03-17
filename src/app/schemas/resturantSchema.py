from pydantic import BaseModel

class Resturant(BaseModel):
    restaurant_id: int = 0
    name: str
    cusine: str
    rating: float = 0
    restaurantAddress: str
    
