from pathlib import Path
from app.db.storage_base import Storage
from app.models import AccountInfo
from fastapi import HTTPException

class AccountsStorage(Storage[AccountInfo]):
    def __init__(self) -> None:
        path = Path(__file__).parent / "accounts.json"
        super().__init__(path)

    def add_new_account(self, user: AccountInfo) -> AccountInfo:
        if self.read(user.username) is not None:
            raise HTTPException(status_code=400, detail="User already exists")

        self.write(user.username, user)
        return user

    def get_account_info(self, username: str) -> AccountInfo | None:
        return self.read(username)
    
    def get_account_role(self, username: str) -> str | None:
        return self.read(username).role