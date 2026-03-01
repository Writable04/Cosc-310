from pathlib import Path
from app.db.storage_base import Storage
from app.models import UserInfo
from fastapi import HTTPException

class AccountsStorage(Storage):
    def __init__(self) -> None:
        path = Path(__file__).parent / "accounts.json"
        super().__init__(path)

    def add_new_user(self, user: UserInfo) -> UserInfo:
        if self.read(user.username) is not None:
            raise HTTPException(status_code=400, detail="User already exists")

        self.write(user.username, user)
        return user

    def get_user_info(self, username: str) -> UserInfo:
        return self.read(username)
    
    def get_user_role(self, username: str) -> str:
        return self.read(username).role