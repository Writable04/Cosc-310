from pydantic import BaseModel

class AccountInfo(BaseModel):
    password: str
    username: str
    role: str