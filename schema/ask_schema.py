from typing import Optional

from pydantic import BaseModel, Field

from schema.message_schema import MessageResponse


# ======================================================
# ASK REQUEST
# ======================================================
from typing import Optional
from pydantic import BaseModel, Field

class AskRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=100000
    )

    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0
    )

    max_tokens: Optional[int] = Field(
        default=None,
        ge=1
    )

    stream: bool = False


class Usage(BaseModel):

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int

    total_cost_usd: float

class AskResponse(BaseModel):

    session_id: str

    title: str

    message: MessageResponse

    provider: str

    model: str

    latency_ms: float

    usage: Usage