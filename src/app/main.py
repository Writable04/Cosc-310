from fastapi import FastAPI
from app import __version__
from app.routers import authentication, dataset, notifications, cart, payment, querys
from app.schemas.baseSchema import HealthResponse

app = FastAPI(
    title="COSC 310 Project",
    version=__version__,
)

@app.get("/")
def root() -> HealthResponse:
    return {"status": "ok", "version": __version__}

app.include_router(dataset.router, prefix="/dataset")
app.include_router(querys.router, prefix="/filters")
app.include_router(authentication.router, prefix="/authentication")
app.include_router(notifications.router, prefix="/notification")
app.include_router(cart.router, prefix="/cart")
app.include_router(payment.router, prefix="/payment")