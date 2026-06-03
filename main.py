from fastapi import FastAPI

from api.user_routes import router as user_router
from api.key_routes import router as key_router
from api.ask_routes import router as ask_router

app = FastAPI()

app.include_router(
    user_router,
    prefix="/users",
    tags=["Users"]
)

app.include_router(
    key_router,
    prefix="/users",
    tags=["API Keys"]
)


app.include_router(
    ask_router,
    prefix="/users",
    tags=["AI"]
)