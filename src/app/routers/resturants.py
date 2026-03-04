from fastapi import APIRouter
from app.schemas.resturantSchema import Resturant
from app.repositories.resturant_repo import load_resturants, save_resturants

router = APIRouter()

resturants = []

resturants = load_resturants()

@router.post("/postResturant")
def post_resturant(resturant: Resturant):
    resturants.append(resturant.dict())
    save_resturants(resturants)
    return resturants

@router.get("/getResturant/{resutrant_id}", response_model=Resturant)
def get_resturant(resturant_id: int):
    return resturants[resturant_id]