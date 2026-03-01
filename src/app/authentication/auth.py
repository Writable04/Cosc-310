from passlib.context import CryptContext
from app.db.storage_accounts import AccountsStorage

class Authentication():
    def __init__(self, storage: AccountsStorage):
        self.pwd_context = CryptContext(schemes=["bcrypt"]) 
        self.storage = storage


    def check_and_encrypt_password(self, password: str) -> str:
        if not self._is_password_valid(password):
            raise ValueError("Password is not valid")

        return self._encrypt_password(password)

    
    def verify_password(self, username: str, password: str) -> bool:
        account_info = self.storage.get_account_info(username)
        if account_info is None:
            return False

        return self.pwd_context.verify(password, account_info.password)
    

    def _is_password_valid(self, password: str) -> bool:
        is_length_valid = len(password) >= 8
        is_contains_uppercase = any(char.isupper() for char in password)
        is_contains_number = any(char.isdigit() for char in password)
        return is_length_valid and is_contains_uppercase and is_contains_number


    def _encrypt_password(self, password: str) -> str:
        return self.pwd_context.hash(password)