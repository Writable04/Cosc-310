from fastapi import APIRouter, Depends, HTTPException

from app.repositories.favourite_repo import FavouriteType
from app.routers.dependencies import favourite_storage, require_auth
from app.schemas.favouriteSchema import UserFavourites

router = APIRouter()


@router.get("/{username}/{token}", dependencies=[Depends(require_auth)])
def get_favourites(username: str) -> dict:
    return favourite_storage.get_favourites_full_data(username)


@router.post("/restaurant/{restaurant_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def add_favourite_restaurant(username: str, restaurant_id: int) -> UserFavourites:
    favourite_restaurant = favourite_storage.add_favourite(username, restaurant_id, FavouriteType.RESTAURANT)
    if favourite_restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return favourite_storage.get_favourites(username)


@router.delete("/restaurant/{restaurant_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def remove_favourite_restaurant(username: str, restaurant_id: int) -> UserFavourites:
    if favourite_storage.remove_favourite(username, restaurant_id, FavouriteType.RESTAURANT) is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return favourite_storage.get_favourites(username)


@router.post("/item/{item_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def add_favourite_item(username: str, item_id: int) -> UserFavourites:
    favourite_item = favourite_storage.add_favourite(username, item_id, FavouriteType.ITEM)
    if favourite_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return favourite_storage.get_favourites(username)


@router.delete("/item/{item_id}/{username}/{token}", dependencies=[Depends(require_auth)])
def remove_favourite_item(username: str, item_id: int) -> UserFavourites:
    if favourite_storage.remove_favourite(username, item_id, FavouriteType.ITEM) is None:
        raise HTTPException(status_code=404, detail="Item not found")
        
    return favourite_storage.get_favourites(username)
