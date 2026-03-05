from pathlib import Path
from app.db.storage_base import Storage

class AccountsStorage(Storage):
    def __init__(self) -> None:
        path = Path(__file__).parent / "accounts.json"
        super().__init__(path)