from fastapi import HTTPException
from passlib.context import CryptContext
from app.db.storage_accounts import AccountsStorage
from uuid import uuid4

class Authentication():
    def __init__(self, storage: AccountsStorage):
        self.encryption = CryptContext(schemes=["bcrypt"]) 
        self.storage = storage


    def encrypt_password(self, password: str) -> str:
        return self.encryption.hash(password)
    

    def verify_password(self, password: str, encrypted_password: str) -> bool:
        return self.encryption.verify(password, encrypted_password)


    def generate_new_token(self) -> str:
        return str(uuid4())


    def authenticate(self, username: str, token: str):
        if self._is_token_valid(username, token):
            return True
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")


    def _is_token_valid(self, username: str, token: str) -> bool:
        account = self.storage.get_account_info(username)
        if account is None:
            return False

        return token == account.token