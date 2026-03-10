from pathlib import Path
import pytest
from app.repositories.storage_base_csv import CSVStorage


@pytest.fixture
def storage(tmp_path):
    file = tmp_path / "test.csv"
    fieldnames = ["id", "name", "cuisine"]
    return CSVStorage(file, fieldnames)

def test_write_and_read(storage):
    storage.write_row({"id": "1", "name": "Pizza Place", "cuisine": "Italian"})

    rows = storage.read_all()

    assert len(rows) == 1
    assert rows[0]["name"] == "Pizza Place"

def test_find_by(storage):
    storage.write_row({"id": "1", "name": "Pizza Place", "cuisine": "Italian"})
    storage.write_row({"id": "2", "name": "Sushi Sai", "cuisine": "Japanese"})

    result = storage.find_by("id", "2")

    assert result is not None
    assert result["name"] == "Sushi Sai"


def test_update(storage):
    storage.write_row({"id": "1", "name": "Pizza Place", "cuisine": "Italian"})

    updated = storage.update("id", "1", {"name": "Better Pizza"})

    assert updated is True
    row = storage.find_by("id", "1")
    assert row["name"] == "Better Pizza"


def test_delete(storage):
    storage.write_row({"id": "1", "name": "Pizza Place", "cuisine": "Italian"})
    storage.write_row({"id": "2", "name": "Sushi Sai", "cuisine": "Japanese"})

    storage.delete("id", "1")

    rows = storage.read_all()

    assert len(rows) == 1
    assert rows[0]["id"] == "2"


def test_overwrite(storage):
    storage.write_row({"id": "1", "name": "Pizza Place", "cuisine": "Italian"})

    new_rows = [
        {"id": "2", "name": "Burger Joint", "cuisine": "American"},
        {"id": "3", "name": "Taco Town", "cuisine": "Mexican"},
    ]

    storage.overwrite(new_rows)

    rows = storage.read_all()

    assert len(rows) == 2
    assert rows[0]["name"] == "Burger Joint"