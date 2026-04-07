from pydantic import BaseModel


class UserFavourites(BaseModel):
    restaurant_ids: list[int] = []
    item_ids: list[int] = []
