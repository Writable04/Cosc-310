from fastapi import FastAPI

from app import __version__
from app.models import HealthResponse

app = FastAPI(
    title="COSC 310 Project",
    version=__version__,
)


@app.get("/")
def root() -> HealthResponse:
    return {"status": "ok", "version": __version__}
