from pydantic import BaseModel

class AccountInfo(BaseModel):
    email: str
    token: str
    password: str
    username: str
    role: str
    address: str = ""
    subscription: int = 0 # 0 = free, 1 = premium, 2 = super premium

class AuthenticationResponse(BaseModel):
    token: str
    status: str
    message: str