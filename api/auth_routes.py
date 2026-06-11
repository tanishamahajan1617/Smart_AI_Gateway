from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from schema.auth_schema import TokenResponse
from core.database import get_db
from models.user_model import User
from sqlalchemy.orm import Session
from service.auth_utils import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        (User.email == form_data.username) |
        (User.username == form_data.username)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"user_id": user.user_id})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }