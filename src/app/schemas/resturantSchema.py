from pydantic import BaseModel

class Resturant(BaseModel):
    restaurant_id: int = 0
    name: str
    cuisine: str
    rating: float = 0
    restaurantAddress: str
    durationMinutes: int = 0
    distanceKM: float = 0.0
    
