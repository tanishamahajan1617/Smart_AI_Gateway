from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class AskRequest(BaseModel):
    query: str


# Response Schema
class AskResponse(BaseModel):
    answer: str
    provider: str
    tokens_used: int

