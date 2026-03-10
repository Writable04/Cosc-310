from pydantic import BaseModel

class AccountInfo(BaseModel):
    email: str
    password: str
    username: str
    role: str