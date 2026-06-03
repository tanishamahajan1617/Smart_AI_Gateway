from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from schema.ask_schema import AskRequest, AskResponse
from data.store import users

from service.classifier import classify_query
from service.token_manager import estimate_tokens
from service.router import select_best_key

router = APIRouter()


async def extract_file_metadata(file: UploadFile):
    content = await file.read()

    metadata = {
        "file_name": file.filename,
        "file_type": file.content_type,
        "file_size": len(content)
    }

    file.file.seek(0)
    return metadata


@router.post(
    "/{user_id}/ask",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK
)
async def ask(
    user_id: str,
    query: str = Form(...),
    file: UploadFile = File(None)
):
    # 🔹 1. Validate user
    user = users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 🔹 2. Handle file
    file_metadata = {}
    if file:
        file_metadata = await extract_file_metadata(file)

    # 🔹 3. Create structured request
    request_data = AskRequest(
        user_id=user_id,
        query=query,
        file_name=file_metadata.get("file_name"),
        file_type=file_metadata.get("file_type"),
        file_size=file_metadata.get("file_size")
    )

    # 🔹 4. Query classification
    query_type = classify_query(request_data.query)

    # 🔹 5. Token estimation
    tokens_needed = estimate_tokens(request_data.query)

    # 🔹 6. Smart routing
    key = select_best_key(
        user["keys"],
        tokens_needed,
        query_type
    )

    if not key:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="All API keys exhausted"
        )

    # 🔹 7. Dummy AI call (replace later)
    response_text = f"[{key['provider']}] response for: {request_data.query}"

    # 🔹 8. Update tokens
    key["used_tokens"] += tokens_needed

    return AskResponse(
        response=response_text,
        provider=key["provider"],
        source="api",
        tokens_used=tokens_needed
    )