from passlib.context import CryptContext
from app.db.storage_accounts import AccountsStorage

class Authentication():
    def __init__(self, storage: AccountsStorage):
        self.encryption = CryptContext(schemes=["bcrypt"]) 
        self.storage = storage


    def encrypt_password(self, password: str) -> str:
        return self.encryption.hash(password)
    

    def verify_password(self, password: str, encrypted_password: str) -> bool:
        return self.encryption.verify(password, encrypted_password)