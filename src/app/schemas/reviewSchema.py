from pydantic import BaseModel

class Review(BaseModel):
    review_id: str = ""
    resturant_id: int
    username: str
    review: str
