from pathlib import Path
from app.repositories.storage_base import Storage
from app.schemas.authenticationSchema import AccountInfo


class AccountsStorage(Storage[AccountInfo]):
    def __init__(self, path: Path | None = None) -> None:
        path = path or Path(__file__).parent.parent / "data/accounts.json"
        super().__init__(path)

    def add_new_account(self, account: AccountInfo) -> AccountInfo:
        if self.read(account.username) is not None:
            raise ValueError("User already exists")

        # Convert the AccountInfo to a JSON string
        account_json = account.model_dump(mode="json")
        self.write(account.username, account_json)
        return account

    def get_account_info(self, username: str) -> AccountInfo | None:
        data = self.read(username)
        if data is None:
            return None
            
        return AccountInfo(**data)
    

    def update_token(self, username: str, token: str) -> None:
        self.update(username, {"token": token})


    def get_account_role(self, username: str) -> str | None:
        data = self.read(username)
        if data is None:
            return None
            
        return AccountInfo(**data).role

    def get_account_email(self, username: str) -> str | None:
        data = self.read(username)
        if data is None:
            return None
            
        return AccountInfo(**data).email

    def get_address(self, username: str) -> str | None:
        data = self.read(username)
        if data is None:
            return None

        return AccountInfo(**data).address

    def get_redeem_choice(self, username: str) -> bool:
        data = self.read(username)
        if data is None:
            return False
        return AccountInfo(**data).redeem_points
 
    def get_reward_points(self, username: str) -> int:
        data = self.read(username)
        if data is None:
            return 0
        return AccountInfo(**data).reward_points
 
    def add_reward_points(self, username: str, points: int) -> int:
        current = self.get_reward_points(username)
        new_total = current + points
        self.update(username, {"reward_points": new_total})
        return new_total
 
    def deduct_reward_points(self, username: str, points: int) -> int:
        current = self.get_reward_points(username)
        new_total = max(current - points, 0)
        self.update(username, {"reward_points": new_total})
        return new_total