from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    version: str

class AccountInfo(BaseModel):
    token: str
    password: str
    username: str
    role: str