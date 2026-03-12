from fastapi import APIRouter
from app.repositories import cart_repo

router = APIRouter()

@router.post("/makeNewCart")
def post_cart(UserID: int):
    return cart_repo.loadUserCart(UserID)
    #return {"message": "done"}
     