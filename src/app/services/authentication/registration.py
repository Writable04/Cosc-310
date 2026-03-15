from app.services.authentication.auth import Authentication
from app.repositories.storage_accounts import AccountsStorage
from app.schemas.authenticationSchema import AccountInfo
import validators

class Registration:
    def __init__(self, storage: AccountsStorage, authentication: Authentication):
        self.storage = storage
        self.authentication = authentication


    def login(self, username: str, password: str, token: str | None = None) -> str:
        if token is None:
            token = self.authentication.generate_new_token()
            self.storage.update_token(username, token)

        account = self.storage.get_account_info(username)
        if account is None:
            raise ValueError("Account not found")

        if not self.authentication.verify_password(password, account.password):
            raise ValueError("Invalid password")

        return token


    def register(self, username: str, password: str, validatated_password: str, role: str, email: str, address: str = "") -> str:
        if self.storage.get_account_info(username) is not None:
            raise ValueError("Username already exists")

        if not self._is_password_valid(password):
            raise ValueError("Password is not valid")
    
        if not self._is_email_valid(email):
            raise ValueError("Email is not valid")

        if password != validatated_password:
            raise ValueError("Passwords do not match")
            
        encrypted_password = self.authentication.encrypt_password(password)
        token = self.authentication.generate_new_token()
        account = AccountInfo(username=username, password=encrypted_password, role=role, email=email, token=token, address=address)

        self.storage.add_new_account(account)

        return self.login(username, password, token)
    
    
    def _is_password_valid(self, password: str) -> bool:
        is_length_valid = len(password) >= 8
        is_contains_uppercase = any(char.isupper() for char in password)
        is_contains_number = any(char.isdigit() for char in password)
        return is_length_valid and is_contains_uppercase and is_contains_number

    def _is_email_valid(self, email: str) -> bool:
        return validators.email(email) is True


