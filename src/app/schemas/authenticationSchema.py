from pydantic import BaseModel

class AccountInfo(BaseModel):
    email: str
    token: str
    password: str
    username: str
    role: str
    address: str = ""
    reward_points: int = 0
    redeem_points: bool = False
    consecutive_password_fails: int = 0
    locked: bool = False
    one_time_code: int = 0
    code_timestamp: float = 0.0

class AuthenticationResponse(BaseModel):
    token: str
    status: str
    message: str