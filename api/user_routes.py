from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from schema.user_schema import ChangePasswordRequest, CreateUserRequest, UpdateUserRequest, UserResponse
from models.user_model import User
from core.database import get_db

from service.auth_utils import verify_password, hash_password, get_current_user


router = APIRouter()


def is_email_taken(email: str, db):
    return db.query(User).filter(User.email == email).first() is not None


def is_username_taken(username: str, db):
    return db.query(User).filter(User.username == username).first() is not None


#CREATE USER
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(req: CreateUserRequest, db:Session = Depends(get_db)):
    # check unique email
    if is_email_taken(req.email, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # check unique username
    if is_username_taken(req.username, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    new_user = User(
        email=req.email,
        username=req.username,
        password=hash_password(req.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        user_id=new_user.user_id,
        email=req.email,
        username=req.username
    )


# GET USER
@router.get("/me", response_model=UserResponse)
def get_user(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == current_user).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    return UserResponse(
        user_id=current_user,
        email=user.email,
        username=user.username
    )

# 🔹 UPDATE USER
@router.patch("/me", response_model=UserResponse)
def update_user(
    req: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.user_id == current_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if req.username:
        user.username = req.username
    if req.email:
        user.email = req.email

    db.commit()
    db.refresh(user)

    return user

#update password
@router.put("/me/password")
def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.user_id == current_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(req.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    user.password = hash_password(req.new_password)

    db.commit()

    return {"message": "Password updated successfully"}


# DELETE USER
@router.delete("/me")
def delete_user(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    user = db.query(User).filter(User.user_id == current_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
