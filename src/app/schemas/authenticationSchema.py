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

class AuthenticationResponse(BaseModel):
    token: str
    status: str
    message: str