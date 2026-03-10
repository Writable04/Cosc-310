from fastapi import APIRouter
from app.schemas.resturantSchema import Resturant
from app.services.dataset.dataset import getItemList
from app.repositories.resturants import new_resturants

router = APIRouter()

resturants = []

@router.post("/postResturant")
def post_resturant(resturant: Resturant):
    resturants.append(resturant.dict())
    new_resturants(resturants)
    return resturants

@router.get("/getResturant/{resutrant_id}", response_model=Resturant)
def get_resturant(resturant_id: int):
    return resturants[resturant_id]

@router.get("/getFoodDelivery/{restrant_id}")
def get_foodDelivery(resturant_id: int):
    return save_foodDelivery(resturant_id)

@router.get("/getFoodItems")
def get_foodItems():
    return getItemList()
