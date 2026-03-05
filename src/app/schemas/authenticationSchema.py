from pydantic import BaseModel

class AccountInfo(BaseModel):
    token: str
    password: str
    username: str
    role: str