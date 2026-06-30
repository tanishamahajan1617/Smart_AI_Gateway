from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from api.user_routes import router as user_router
from api.key_routes import router as key_router
from api.ask_routes import router as ask_router
from api.auth_routes import router as auth_router
from api.session_routes import router as session_router
from core.database import engine, Base

from models.user_model import User
from models.api_key import APIKey
from models.gatewayLog import Conversation
from core.model_registary import load_model_registry

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Load model registry once on startup
    load_model_registry()
    print("Model registry loaded.")

    yield

    # Shutdown logic (future use)
    print("Application shutting down.")


app = FastAPI(lifespan=lifespan)

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



app.include_router(
    session_router,
    prefix="/sessions",
    tags=["Sessions"]
)

app.include_router(auth_router)

