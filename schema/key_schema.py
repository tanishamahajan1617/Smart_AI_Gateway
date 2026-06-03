from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class AddKeyRequest(BaseModel):
    provider: str = Field(..., min_length=2, max_length=50)
    api_key: str = Field(..., min_length=10)
    limit: int = Field(..., gt=0)

    # Optional future features
    priority: Optional[int] = Field(default=1, ge=1, le=5)
    name: Optional[str] = Field(default=None, max_length=50)

    @field_validator("provider")
    @classmethod
    def clean_provider(cls, v: str):
        v = v.strip().lower()
        if not v:
            raise ValueError("Provider cannot be empty")
        return v

    @field_validator("api_key")
    @classmethod
    def clean_api_key(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("API key cannot be empty")
        return v

    @field_validator("name")
    @classmethod
    def clean_name(cls, v):
        if v:
            v = v.strip()
        return v
class KeyResponse(BaseModel):
    key_id: int
    provider: str
    used_tokens: int
    limit: int
    remaining_tokens: int
    priority: int
    name: Optional[str]


class AddKeyResponse(BaseModel):
    message: str
    key_id: int


class GetKeysResponse(BaseModel):
    keys: List[KeyResponse]


class DeleteKeyResponse(BaseModel):
    message: str