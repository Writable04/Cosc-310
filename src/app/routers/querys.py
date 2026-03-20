from fastapi import APIRouter, HTTPException
from app.schemas.resturantSchema import Resturant
from app.schemas.menuSchema import Menu
from app.schemas.itemSchema import Item
from app.routers.dependencies import resturant_storage, menu_storage, item_storage
from app.services.dataset.querys import filter_resturants 

router = APIRouter()



@router.get("/filterResturant")
def filterResturants(
    name: str = None,
    cuisine: str = None,
    rating: float = 0,
    distance: float = 0
):
    return filter_resturants(
        resturant_storage,
        name=name,
        cuisine=cuisine,
        rating=rating,
        distance=distance
    )

