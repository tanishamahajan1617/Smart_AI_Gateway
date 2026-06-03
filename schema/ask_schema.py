from pydantic import BaseModel, Field
from typing import Optional


class AskRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)

    # file metadata (not actual file)
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None


class AskResponse(BaseModel):
    response: str
    provider: str
    source: str
    tokens_used: int