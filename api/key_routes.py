from fastapi import APIRouter, HTTPException, status
from schema.key_schema import (
    AddKeyRequest,
    AddKeyResponse,
    GetKeysResponse,
    DeleteKeyResponse,
    KeyResponse
)
from data.store import users

router = APIRouter()


# 🔹 Add API Key
@router.post(
    "/{user_id}/keys",
    response_model=AddKeyResponse,
    status_code=status.HTTP_201_CREATED
)
def add_key(user_id: str, req: AddKeyRequest):
    user = users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    key_id = user["next_key_id"]

    key = {
        "key_id": key_id,
        "provider": req.provider,
        "api_key": req.api_key,
        "used_tokens": 0,
        "limit": req.limit,
        "priority": req.priority,
        "name": req.name
    }

    user["keys"].append(key)
    user["next_key_id"] += 1

    return AddKeyResponse(
        message="Key added successfully",
        key_id=key_id
    )


# 🔹 Get All Keys
@router.get(
    "/{user_id}/keys",
    response_model=GetKeysResponse,
    status_code=status.HTTP_200_OK
)
def get_keys(user_id: str):
    user = users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    keys = [
        KeyResponse(
            key_id=k["key_id"],
            provider=k["provider"],
            used_tokens=k["used_tokens"],
            limit=k["limit"],
            remaining_tokens=k["limit"] - k["used_tokens"],
            priority=k.get("priority", 1),
            name=k.get("name")
        )
        for k in user["keys"]
    ]

    return GetKeysResponse(keys=keys)


# 🔹 Delete API Key
@router.delete(
    "/{user_id}/keys/{key_id}",
    response_model=DeleteKeyResponse,
    status_code=status.HTTP_200_OK
)
def delete_key(user_id: str, key_id: int):
    user = users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    key_exists = any(k["key_id"] == key_id for k in user["keys"])
    if not key_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    user["keys"] = [k for k in user["keys"] if k["key_id"] != key_id]

    return DeleteKeyResponse(message="Key deleted successfully")