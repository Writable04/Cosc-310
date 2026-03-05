from pathlib import Path
import pytest
from app.data.db.storage_base import Storage

@pytest.fixture
def storage(tmp_path: Path) -> Storage:
    return Storage(tmp_path / "test.json")


def test_read_nonexistent_key(storage: Storage) -> None:
    assert storage.read("any") is None


def test_write_overwrites(storage: Storage) -> None:
    storage.write("a", 1)
    storage.write("a", 2)
    assert storage.read("a") == 2


@pytest.mark.parametrize(
    "value",
    ["hello", 42, 3.14, True, [1, 2, 3], {"x": 1, "y": 2}, None],
)
def test_write_read_types(storage: Storage, value: str | int | float | bool | list | dict | None) -> None:
    storage.write("key", value)
    assert storage.read("key") == value


def test_update_merge_dicts(storage: Storage) -> None:
    storage.write("a", {"x": 1})
    storage.update("a", {"y": 2})
    assert storage.read("a") == {"x": 1, "y": 2}
