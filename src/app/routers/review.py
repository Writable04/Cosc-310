from fastapi import APIRouter, HTTPException
from app.repositories.review_repo import ReviewStorage
from app.schemas.reviewSchema import Review
from typing import List


router = APIRouter()
storage = ReviewStorage()


@router.post("/reviews", response_model=Review)
def create_review(review: Review):
    try:
        return storage.new_review(review)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/reviews", response_model=List[Review])
def get_all_reviews():
    data = storage._load()
    return [Review(**item) for item in data.values()]


@router.get("/reviews/restaurant/{resturant_id}", response_model=List[Review])
def get_reviews_by_resturant_id(resturant_id: int):
    return storage.find_reviews_by_resturant_id(resturant_id)


@router.get("/reviews/{review_id}", response_model=Review)
def get_review(review_id: str):
    review = storage.find_review(review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.delete("/reviews/{review_id}")
def delete_review(review_id: str):
    try:
        storage.remove_review(review_id)
        return {"status": "success", "message": "Review deleted successfully"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
