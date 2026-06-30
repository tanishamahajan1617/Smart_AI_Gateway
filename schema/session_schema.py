from datetime import datetime
from typing import List, Optional
from schema.message_schema import MessageResponse
from pydantic import BaseModel, Field

class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Chat"


class CreateSessionResponse(BaseModel):
    session_id: str
    title: str


class UpdateSessionRequest(BaseModel):
    title: str


class SessionResponse(BaseModel):
    session_id: str
    title: str

    created_at: datetime
    updated_at: datetime


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]


# ==================================
# CHAT HISTORY
# ==================================


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageResponse]


# ==================================
# DELETE SESSION
# ==================================

class DeleteSessionResponse(BaseModel):
    success: bool
    message: str