from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from service.auth_utils import get_current_user

from models.user_model import User

from schema.ask_schema import (
    AskRequest,
    AskResponse
)

from service.ask_service import AskService


router = APIRouter(
    prefix="/ask",
)


@router.post(
    "",
    response_model=AskResponse
)
def ask(
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AskResponse:
    """
    Start a new conversation.
    """

    return AskService.start_chat(
        db=db,
        user_id=current_user,
        request=request
    )