from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class MessageResponse(BaseModel):

    id: str

    session_id: str

    role: Literal[
        "user",
        "assistant",
        "system"
    ]

    content: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )