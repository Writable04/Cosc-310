import json
from pathlib import Path
from typing import Generic, TypeVar

T = TypeVar("T")


class Storage(Generic[T]):
    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self, key: str) -> T | None:
        data = self._load()
        return data.get(key)

    def write(self, key: str, value: T) -> None:
        data = self._load()
        data[key] = value
        self._save(data)

    def update(self, key: str, value: T) -> None:
        data = self._load()
        existing = data.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            data[key] = {**existing, **value}
        else:
            data[key] = value

        self._save(data)

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        with open(self.path, "r") as storage:
            return json.load(storage)

    def _save(self, data: dict) -> None:
        with open(self.path, "w") as storage:
            json.dump(data, storage, indent=2)
