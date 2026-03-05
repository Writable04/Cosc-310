from fastapi import FastAPI

from app import __version__
from fastapi import FastAPI
from app.routers import resturants
from app.routers import authentication

app = FastAPI(
    title="COSC 310 Project",
    version=__version__,
)


@app.get("/")
def root() -> dict:
    return {"status": "ok", "version": __version__}


app.include_router(resturants.router, prefix = "/resturants")
app.include_router(authentication.router, prefix = "/authentication")