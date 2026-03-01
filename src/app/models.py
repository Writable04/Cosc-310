from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    version: str

class UserInfo(BaseModel):
    password: str
    username: str
    role: str