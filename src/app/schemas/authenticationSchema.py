from pydantic import BaseModel

class AccountInfo(BaseModel):
    email: str
    token: str
    password: str
    username: str
    role: str
    address: str = ""

class AuthenticationResponse(BaseModel):
    token: str
    status: str
    message: str