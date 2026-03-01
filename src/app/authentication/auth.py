from passlib.context import CryptContext
from app.db.storage_accounts import AccountsStorage

class Authentication():
    def __init__(self, storage: AccountsStorage):
        self.pwd_context = CryptContext(schemes=["bcrypt"]) 
        self.storage = storage

    def encrypt_password(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def verify_password(self, username: str, password: str) -> bool:
        account_info = self.storage.get_account_info(username)
        if account_info is None:
            return False

        return self.pwd_context.verify(password, account_info.password)