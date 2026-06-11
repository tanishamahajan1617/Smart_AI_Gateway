from fastapi import FastAPI

from api.user_routes import router as user_router
from api.key_routes import router as key_router
from api.ask_routes import router as ask_router
from api.auth_routes import router as auth_router
from core.database import engine, Base

from models.user_model import User
from models.key_model import APIKey
from models.conversation import Conversation


app = FastAPI()
Base.metadata.create_all(bind=engine)

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

app.include_router(auth_router)