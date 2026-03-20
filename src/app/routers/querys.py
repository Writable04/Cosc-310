from fastapi import APIRouter, Depends, HTTPException
from app.schemas.resturantSchema import Resturant
from app.schemas.menuSchema import Menu
from app.schemas.itemSchema import Item
from app.routers.dependencies import accounts_storage, require_auth, resturant_storage
from app.services.dataset.querys import filter_resturants 

router = APIRouter()

@router.get("/filterResturant/{username}/{token}" , dependencies=[Depends(require_auth)])
def filterResturants(
    username: str,
    name: str = None,
    cuisine: str = None,
    rating: float = 0,
    distance: float = 0
):
    user_address = accounts_storage.get_address(username) if username is not None and username != "" else None
    return filter_resturants(
        resturant_storage,
        user_address=user_address,
        name=name,
        cuisine=cuisine,
        rating=rating,
        distance=distance
    )
