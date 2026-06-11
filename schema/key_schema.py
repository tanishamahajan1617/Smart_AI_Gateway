from pydantic import BaseModel, Field
from typing import Optional


class AddKeyRequest(BaseModel):
    provider: str
    api_key: str
    priority: Optional[int] = 1
    limit: Optional[int] = None


class KeyResponse(BaseModel):
    key_id: str
    provider: str
    priority: int
    used_tokens: int
    limit: Optional[int]
    status: str