from fastapi import APIRouter, status
from schema.user_schema import CreateUserRequest
from data.store import users

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_user(req: CreateUserRequest):
    if req.user_id in users:
        return {"message": "User already exists"}

    users[req.user_id] = {
        "keys": [],
        "next_key_id": 1
    }

    return {"message": "User created successfully"}