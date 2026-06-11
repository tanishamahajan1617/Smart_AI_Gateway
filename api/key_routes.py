from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from models.key_model import APIKey   
from models.user_model import User
from schema.key_schema import AddKeyRequest, KeyResponse
from service.auth_utils import get_current_user

router = APIRouter()


# 🔹 ADD KEY
@router.post("/keys", response_model=KeyResponse)
def add_key(
    req: AddKeyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.user_id if isinstance(current_user, User) else current_user
    new_key = APIKey(
        user_id=user_id,
        provider=req.provider,
        api_key=req.api_key,
        priority=req.priority,
        limit=req.limit
    )

    db.add(new_key)
    db.commit()
    db.refresh(new_key)

    return KeyResponse(
        key_id=new_key.key_id,
        provider=new_key.provider,
        priority=new_key.priority,
        used_tokens=new_key.used_tokens,
        limit=new_key.limit,
        status=new_key.status
    )


# 🔹 GET KEYS
@router.get("/keys", response_model=list[KeyResponse])
def get_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if isinstance(current_user, User):
        keys = current_user.keys
    else:
        user = db.query(User).filter(User.user_id == current_user).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        keys = user.keys

    return [
        KeyResponse(
            key_id=k.key_id,
            provider=k.provider,
            priority=k.priority,
            used_tokens=k.used_tokens,
            limit=k.limit,
            status=k.status
        )
        for k in keys
    ]


# 🔹 DELETE KEY
@router.delete("/keys/{key_id}")
def delete_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.user_id if isinstance(current_user, User) else current_user
    key = db.query(APIKey).filter(
        APIKey.key_id == key_id,
        APIKey.user_id == user_id
    ).first()

    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key not found"
        )

    db.delete(key)
    db.commit()

    return {"message": "Key deleted successfully"}