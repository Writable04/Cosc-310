from pathlib import Path
from app.repositories.storage_base import Storage
from app.schemas.authenticationSchema import AccountInfo
from app.services.authentication.auth import Authentication
from app.repositories.storage_accounts import AccountsStorage
from app.services.notifications.notifications import Notification
from datetime import datetime
import random

class ResetPassword():
    def __init__(self, storage:AccountsStorage, authentication:Authentication, notification: Notification):
        self.storage = storage
        self.authentication = authentication
        self.notification = notification

    def update_login_fails(self, username:str):
        data = self.storage.read(username)
        data["consecutive_password_fails"] += 1
        self.storage.write(username, data)
        return AccountInfo(**data).consecutive_password_fails
    
    def reset_login_fails(self, username:str):
        data = self.storage.read(username)
        data["consecutive_password_fails"] == 0
        self.storage.write(username, data)
        return AccountInfo(**data).consecutive_password_fails
    
    def reset_password(self, username: str, new_password: str, validated_password: str, one_time_code: int):
        EXPIRY_SECONDS = 600 # ten minutes
        data = self.storage.read(username)
        self.send_one_time_code(username)

        if (not one_time_code) or (one_time_code != data["one_time_code"]):
            raise ValueError("Incorrect code. Please try again")
        
        if one_time_code and ((datetime.now().timestamp() - data["code_timestamp"]) > EXPIRY_SECONDS) :
            raise ValueError("Code has expired.")
        
        if new_password != validated_password:
            raise ValueError("Passwords do not match")
        
        # this returns true if the new password is the same as the priorly hashed one
        if self.authentication.verify_password(new_password, data["password"]):
            raise ValueError("New password must be different from old one. Please try again")
        
        if not self._is_password_valid(new_password):
            raise ValueError("Password must be 8+ characters, and contain an uppercase letter and a numerical digit.")

        new_encrypted_password = self.authentication.encrypt_password(new_password)
        token = self.authentication.generate_new_token()
        data["password"] = new_encrypted_password
        data["token"] = token
        data["consecutive_password_fails"] = 0
        data["one_time_code"] = 0
        data["code_timestamp"] = 0.0
        data["locked"] = False
        
        self.storage.write(username, data)
        return "Password Successfully Reset." # this could probably be done better

    def send_one_time_code(self, username: str):
        data = self.storage.read(username)
        code = random.randint(100000, 999999)
        
        # email notify the user
        subject = "Your One Time Verification Code"
        msg = (f"your verification code is: {code}.\nDo not share this code with anyone. \nThe code will expire in ten minutes.")
        email = data["email"]
        self.notification.send_notification(subject=subject, message=msg, receiver_email=email)
        
        # generate a timestamp
        data["code_timestamp"] = datetime.now().timestamp()
        data["one_time_code"] = code
        self.storage.write(username, data)
        return True
        
    def _is_password_valid(self, password: str) -> bool:
        is_length_valid = len(password) >= 8
        is_contains_uppercase = any(char.isupper() for char in password)
        is_contains_number = any(char.isdigit() for char in password)
        return is_length_valid and is_contains_uppercase and is_contains_number
    # i copy pasted this method to avoid circular imports between this repo and registration.py 