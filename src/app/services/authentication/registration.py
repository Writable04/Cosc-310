from app.services.authentication.auth import Authentication
from app.repositories.storage_accounts import AccountsStorage
from app.schemas.authenticationSchema import AccountInfo
import validators

class Registration:
    def __init__(self, storage: AccountsStorage, authentication: Authentication):
        self.storage = storage
        self.authentication = authentication

    def register(self, username: str, password: str, validatated_password: str, role: str, email: str) -> AccountInfo:
        if self.storage.get_account_info(username) is not None:
            raise ValueError("Username already exists")

        if not self._is_password_valid(password):
            raise ValueError("Password is not valid")
    
        if not self._is_email_valid(email):
            raise ValueError("Email is not valid")

        if password != validatated_password:
            raise ValueError("Passwords do not match")
        
        encrypted_password = self.authentication.encrypt_password(password)
        account = AccountInfo(username=username, password=encrypted_password, role=role, email=email)

        return self.storage.add_new_account(account)
    
    
    def _is_password_valid(self, password: str) -> bool:
        is_length_valid = len(password) >= 8
        is_contains_uppercase = any(char.isupper() for char in password)
        is_contains_number = any(char.isdigit() for char in password)
        return is_length_valid and is_contains_uppercase and is_contains_number

    def _is_email_valid(self, email: str) -> bool:
        return validators.email(email) is True
