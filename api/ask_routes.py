from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from core.database import get_db
from service.auth_utils import get_current_user

from models.key_model import APIKey
from models.conversation import Conversation

from schema.ask_schema import AskResponse


router = APIRouter(prefix="/ask")


@router.post("/", response_model=AskResponse)
async def ask(
    query: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Step 1: Get active API key for logged-in user
    key = db.query(APIKey).filter(
        APIKey.user_id == current_user,
        APIKey.status == "active"
    ).first()

    if not key:
        raise HTTPException(
            status_code=400,
            detail="No active API keys found"
        )

    # Step 2: Detect file type
    file_type = file.content_type if file else "text"

    # Step 3: Dummy response (EDA phase)
    response_text = f"Processed query: {query}"

    # Step 4: Token calculation
    tokens_used = len(query.split()) * 2

    #  Step 5: Update key usage
    key.used_tokens += tokens_used

    # Step 6: Save conversation (EDA logs )
    conversation = Conversation(
        user_id=current_user,   # auto from JWT
        query=query,
        response=response_text,
        provider=key.provider,
        tokens_used=tokens_used,
        file_type=file_type,
        query_length=len(query.split()),
        selected_priority=key.priority
    )

    db.add(conversation)
    db.commit()

    # Step 7: Return response
    return AskResponse(
        answer=response_text,
        provider=key.provider,
        tokens_used=tokens_used
    )