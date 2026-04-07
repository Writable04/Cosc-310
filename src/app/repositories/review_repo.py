from pathlib import Path
from app.schemas.reviewSchema import Review
from app.repositories.storage_base import Storage
from uuid import uuid4


class ReviewStorage(Storage[dict]):
    def __init__(self, path: Path | None = None):
        path = path or Path(__file__).parent.parent / "data/resturantData/reviews.json"
        super().__init__(path)

    def new_review(self, review: Review) -> Review:
        review_id = str(uuid4())
        review.review_id = review_id
        self.write(review_id, review.model_dump())
        return review

    def find_review(self, review_id: str) -> Review | None:
        data = self.read(str(review_id))
        if data:
            return Review(**data)
        return None

    def find_reviews_by_resturant_id(self, resturant_id: int) -> list[Review]:
        data = self._load()
        return [
            Review(**review_data)
            for review_data in data.values()
            if review_data.get("resturant_id") == resturant_id
        ]

    def remove_review(self, review_id: str) -> None:
        data = self._load()
        if str(review_id) in data:
            del data[str(review_id)]
            self._save(data)
        else:
            raise ValueError("Review not found")
