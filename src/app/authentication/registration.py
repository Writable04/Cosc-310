from app.authentication.auth import Authentication
from app.db.storage_accounts import AccountsStorage
from app.models import AccountInfo


class Registration:
    def __init__(self, storage: AccountsStorage, authentication: Authentication):
        self.storage = storage
        self.authentication = authentication


    def login(self, username: str, password: str) -> AccountInfo:
        account = self.storage.get_account_info(username)
        if account is None:
            raise ValueError("Account not found")

        if not self.authentication.verify_password(password, account.password):
            raise ValueError("Invalid password")

        # Return the encrypted password to be used as authentication token
        return account.password


    def register(self, username: str, password: str, validatated_password: str, role: str) -> AccountInfo:
        if self.storage.get_account_info(username) is not None:
            raise ValueError("Username already exists")

        if not self._is_password_valid(password):
            raise ValueError("Password is not valid")

        if password != validatated_password:
            raise ValueError("Passwords do not match")
        
        encrypted_password = self.authentication.encrypt_password(password)
        account = AccountInfo(username=username, password=encrypted_password, role=role)

        self.storage.add_new_account(account)

        return self.login(username, password)
    
    
    def _is_password_valid(self, password: str) -> bool:
        is_length_valid = len(password) >= 8
        is_contains_uppercase = any(char.isupper() for char in password)
        is_contains_number = any(char.isdigit() for char in password)
        return is_length_valid and is_contains_uppercase and is_contains_number

