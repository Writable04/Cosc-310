from passlib.context import CryptContext
from app.repositories.storage_accounts import AccountsStorage

class Authentication():
    def __init__(self, storage: AccountsStorage):
        self.encryption = CryptContext(schemes=["bcrypt"]) 
        self.storage = storage


    def encrypt_password(self, password: str) -> str:
        return self._encrypt_password(password)

    
    def verify_password(self, username: str, password: str) -> bool:
        account_info = self.storage.get_account_info(username)
        if account_info is None:
            return False

        return self.encryption.verify(password, account_info.password)
    

    def _encrypt_password(self, password: str) -> str:
        return self.encryption.hash(password)