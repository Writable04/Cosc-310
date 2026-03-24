from fastapi import APIRouter, Depends
from app.routers.dependencies import accounts_storage, require_auth, resturant_storage
from app.services.dataset.querys import filter_resturants

router = APIRouter()

@router.get("/resturants/{username}/{token}" , dependencies=[Depends(require_auth)])
def get_filtered_restaurants(
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
