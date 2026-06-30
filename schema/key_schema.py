from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# ADD API KEY
# ==========================================================

class AddKeyRequest(BaseModel):

    provider: str = Field(
        ...,
        example="openai"
    )

    api_key: str = Field(
        ...,
        example="sk-xxxxxxxx"
    )

    # Optional:
    # If provided -> save only this model
    # If omitted -> discover all available models
    model: Optional[str] = Field(
        default=None,
        example="gpt-4o"
    )

    priority: int = Field(
        default=3,
        ge=1,
        le=5
    )

    limit: Optional[int] = Field(
        default=None,
        ge=1
    )


# ==========================================================
# MODEL RESPONSE
# ==========================================================

class ModelResponse(BaseModel):

    model_id: str

    model: str

    context_window: Optional[int]

    speed: Optional[float]

    latency: Optional[float]

    mmlu_score: Optional[float]

    arena_score: Optional[float]

    price_per_million_tokens: Optional[float]

    quality_rating: Optional[int]

    speed_rating: Optional[int]

    price_rating: Optional[int]

    open_source: Optional[bool]

    tokens_used: int

    status: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# API KEY RESPONSE
# ==========================================================

class KeyResponse(BaseModel):

    key_id: str

    provider: str

    api_key: str

    priority: int

    limit: Optional[int]

    status: str

    created_at: datetime

    updated_at: datetime

    models: list[ModelResponse]

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# SIMPLE MESSAGE RESPONSE
# ==========================================================

class MessageResponse(BaseModel):
    message: str


# ==========================================================
# UPDATE API KEY
# ==========================================================

class UpdateKeyRequest(BaseModel):

    priority: Optional[int] = Field(
        default=None,
        ge=1,
        le=5
    )

    limit: Optional[int] = Field(
        default=None,
        ge=1
    )

    status: Optional[str] = Field(
        default=None,
        examples=["active"]
    )