import json

from fastapi.testclient import TestClient

from app.main import app
from app.repositories.review_repo import ReviewStorage
from app.routers import review as review_router


def test_find_reviews_by_resturant_id(tmp_path) -> None:
    test_file = tmp_path / "reviews.json"
    test_file.write_text(
        json.dumps(
            {
                "review1": {
                    "review_id": "review1",
                    "resturant_id": 1,
                    "username": "bob",
                    "review": "Great burger.",
                },
                "review2": {
                    "review_id": "review2",
                    "resturant_id": 2,
                    "username": "leyla",
                    "review": "Nice tacos.",
                },
                "review3": {
                    "review_id": "review3",
                    "resturant_id": 1,
                    "username": "tolu",
                    "review": "Fast delivery.",
                },
            },
            indent=2,
        )
    )

    storage = ReviewStorage(path=test_file)

    reviews = storage.find_reviews_by_resturant_id(1)

    assert len(reviews) == 2
    assert all(review.resturant_id == 1 for review in reviews)
    assert [review.review_id for review in reviews] == ["review1", "review3"]

