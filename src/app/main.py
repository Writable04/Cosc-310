from fastapi import FastAPI
from app import __version__
from app.routers import authentication, dataset, notifications, cart, payment, checkout, querys, delivery, review, favourites
from app.schemas.baseSchema import HealthResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="COSC 310 Project",
    version=__version__,
)
# front end 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(checkout.router, prefix="/checkout")
app.include_router(delivery.router, prefix="/delivery")
app.include_router(review.router, prefix="/review")
app.include_router(favourites.router, prefix="/favourites")
