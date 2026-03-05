from fastapi import FastAPI

from app import __version__
from app.repositories.storage_accounts import AccountsStorage
from app.routers import resturants
from app.routers import authentication
from app.schemas.baseSchema import HealthResponse
from app.services.authentication.auth import Authentication

app = FastAPI(
    title="COSC 310 Project",
    version=__version__,
)

storage = AccountsStorage()
authentication = Authentication(storage)


def require_auth(username: str, token: str):
    authentication.authenticate(username, token)
    return True


@app.get("/")
def root() -> HealthResponse:
    return {"status": "ok", "version": __version__}


app.include_router(resturants.router, prefix = "/resturants")
app.include_router(authentication.router, prefix = "/authentication")
