from fastapi import FastAPI

from app import __version__
from app.models import HealthResponse
from fastapi import FastAPI
from app.routers import resturants


app = FastAPI(
    title="COSC 310 Project",
    version=__version__,
)

app.include_router(resturants.router, prefix = "/resturants")

@app.get("/")
def root() -> HealthResponse:
    return {"status": "ok", "version": __version__}
