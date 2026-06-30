from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db

from models.session_model import Session as SessionModel
from models.message_model import Message
from schema.ask_schema import AskRequest,AskResponse
from schema.session_schema import (
    CreateSessionRequest,
    CreateSessionResponse,
    SessionResponse,
    SessionListResponse,
    ChatHistoryResponse,
    DeleteSessionResponse
)

from service.auth_utils import get_current_user
from service.ask_service import AskService

router = APIRouter()

@router.post("/{session_id}/ask", response_model=AskResponse)
def continue_chat(
    session_id: str,
    request: AskRequest,
    
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return AskService.continue_chat(
        db=db,
        user_id=current_user,
        session_id=session_id,
        request=request,
       
    )
# ==================================
# CREATE SESSION
# ==================================

@router.post("/", response_model=CreateSessionResponse)
def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):

    session = SessionModel(
        user_id=user_id,
        title=request.title
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


# ==================================
# GET ALL SESSIONS
# ==================================
@router.get("/", response_model=SessionListResponse)
def get_sessions(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):

    sessions = (
        db.query(SessionModel)
        .filter(
            SessionModel.user_id == user_id
        )
        .order_by(
            SessionModel.updated_at.desc()
        )
        .all()
    )

    return {
        "sessions": sessions
    }


# ==================================
# GET SINGLE SESSION
# ==================================

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):

    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.session_id == session_id,
            SessionModel.user_id == user_id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session


# ==================================
# GET CHAT HISTORY
# ==================================

@router.get(
    "/{session_id}/history",
    response_model=ChatHistoryResponse
)
def get_history(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):

    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.session_id == session_id,
            SessionModel.user_id == user_id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    messages = (
        db.query(Message)
        .filter(
            Message.session_id == session_id
        )
        .order_by(
            Message.created_at.asc()
        )
        .all()
    )

    return {
        "session_id": session_id,
        "messages": messages
    }
# ==================================
# DELETE SESSION
# ==================================

@router.delete(
    "/{session_id}",
    response_model=DeleteSessionResponse
)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):

    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.session_id == session_id,
            SessionModel.user_id == user_id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    db.delete(session)
    db.commit()

    return {
        "success": True,
        "message": "Session deleted successfully"
    }