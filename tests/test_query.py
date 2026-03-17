import pytest
from app.services.dataset.querys import filter_resturants

class MockStorage:
    def __init__(self, data):
        self._data = data
    def read_all(self):
        return self._data


@pytest.fixture
def storage():
    return MockStorage([
        {"restaurant_id": 1, "name": "Bobs Burgers", "cuisine": "American", "rating": 4.5, "restaurantAddress": "123 A St"},
        {"restaurant_id": 2, "name": "Tommys Tacos", "cuisine": "Mexican", "rating": 4.9, "restaurantAddress": "456 B St"},
        {"restaurant_id": 3, "name": "Pauls Pizza", "cuisine": "Italian", "rating": 2.0, "restaurantAddress": "789 C St"},
        {"restaurant_id": 4, "name": "Pops Pizza", "cuisine": "Italian", "rating": 5.0, "restaurantAddress": "321 D St"},
    ])

def test_no_filters_returns_all(storage):
    results = filter_resturants(storage)
    assert len(results) == 4


def test_filter_by_cuisine(storage):
    results = filter_resturants(storage, cuisine="italian")
    assert len(results) == 2


#def test_filter_by_distance(storage):
#   results = filter_resturants(storage, distance=5)
#    assert len(results) == 2


def test_filter_by_rating(storage):
    results = filter_resturants(storage, rating=4.5)
    assert len(results) == 3


def test_filter_by_name_partial(storage):
    results = filter_resturants(storage, name="pizza")
    names = [r.name for r in results]
    assert "Pauls Pizza" in names
    assert "Pops Pizza" in names


def test_combined_filters(storage):
    results = filter_resturants(storage, cuisine="american", rating=4.0)
    assert len(results) == 1
    assert results[0].name == "Bobs Burgers"
