import hashlib
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session,selectinload

from core.database import get_db
from core.encrypt import encrypt_key, decrypt_key
from core.model_registary import get_model_capabilities,clean,load_model_registry,infer_capabilities
from core.secure_keys import mask_key
from discovery.discovery_factory import DiscoveryFactory

from models.api_key import APIKey
from models.api_key_models import APIKeyModel
from core.model_filter import ModelFilter
from schema.key_schema import (
    AddKeyRequest,
    KeyResponse,
    MessageResponse,
    UpdateKeyRequest
)

from service.auth_utils import get_current_user
from service.key_service import build_key_response
from typing import Optional

from core.model_registary import clean

router = APIRouter()


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def generate_key_hash(api_key: str) -> str:
    

    return hashlib.sha256(
        api_key.encode()
    ).hexdigest()


def validate_api_key(api_key: str):
   

    if len(api_key.strip()) < 10:

        raise HTTPException(
            status_code=400,
            detail="Invalid API key."
        )


def validate_status(status: str):

    allowed = [
        "active",
        "inactive"
    ]

    if status not in allowed:

        raise HTTPException(
            status_code=400,
            detail="Invalid status."
        )

  


def resolve_models(
    provider: str,
    api_key: str,
    requested_model: str | None = None,
) -> list[str]:

    provider = provider.strip().lower()

    # User selected a specific model
    if requested_model:
        return [requested_model.strip()]

    # Automatic discovery
    discovery = DiscoveryFactory.create(
        provider=provider,
        api_key=api_key,
    )

    return discovery.list_models()
# ==========================================================
# ADD API KEY
# ==========================================================

@router.post("/", response_model=KeyResponse)
def add_api_key(
    request: AddKeyRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    # ------------------------------------------------------
    # Validate API Key
    # ------------------------------------------------------

    validate_api_key(request.api_key)

    provider = clean(request.provider)

    api_key_hash = generate_key_hash(
        request.api_key
    )

    # ------------------------------------------------------
    # Existing API Key
    # ------------------------------------------------------

    key = (
        db.query(APIKey)
        .filter(
            APIKey.user_id == user,
            APIKey.provider == provider,
            APIKey.api_key_hash == api_key_hash
        )
        .first()
    )

    # ------------------------------------------------------
    # Create Parent Key (Only if new)
    # ------------------------------------------------------

    if key is None:

        encrypted_key = encrypt_key(
            request.api_key
        )

        key = APIKey(

            user_id=user,

            provider=provider,

            api_key=encrypted_key,

            api_key_hash=api_key_hash,

            priority=request.priority,

            limit=request.limit,

            status="active"

        )

        db.add(key)

        db.flush()

    # ------------------------------------------------------
    # Resolve Models
    # ------------------------------------------------------

    models = resolve_models(

        provider=provider,

        api_key=request.api_key,

        requested_model=request.model

    )

    models = list(dict.fromkeys(models))
    models = ModelFilter.filter(models)

    if not models:

        raise HTTPException(
            status_code=400,
            detail="No models found."
        )

    # ------------------------------------------------------
    # Save Models
    # ------------------------------------------------------

    for model in models:

        model = clean(model)

        # Skip if already linked
        exists = (
            db.query(APIKeyModel)
            .filter(
                APIKeyModel.key_id == key.key_id,
                APIKeyModel.model == model
            )
            .first()
        )

        if exists:
            continue

        capabilities = get_model_capabilities(
            provider,
            model
        )

        if capabilities is None:

            capabilities = infer_capabilities(
                provider,
                model
            )

        db.add(

            APIKeyModel(

                key_id=key.key_id,

                model=model,

                context_window=capabilities.get(
                    "context_window"
                ),

                speed=capabilities.get(
                    "speed"
                ),

                latency=capabilities.get(
                    "latency"
                ),

                mmlu_score=capabilities.get(
                    "mmlu_score"
                ),

                arena_score=capabilities.get(
                    "arena_score"
                ),

                price_per_million_tokens=capabilities.get(
                    "price_per_million_tokens"
                ),

                quality_rating=capabilities.get(
                    "quality_rating"
                ),

                speed_rating=capabilities.get(
                    "speed_rating"
                ),

                price_rating=capabilities.get(
                    "price_rating"
                ),

                open_source=capabilities.get(
                    "open_source"
                ),

                tokens_used=0,

                status="active"

            )

        )

    # ------------------------------------------------------
    # Commit
    # ------------------------------------------------------

    try:

        db.commit()

        db.refresh(key)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save API key."
        )

    return build_key_response(key)



# ==========================================================
# GET ALL API KEYS
# ==========================================================

@router.get("/", response_model=list[KeyResponse])
def get_keys(
    status: str = "active",
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    query = (
        db.query(APIKey)
        .options(
            selectinload(APIKey.models)
        )
        .filter(
            APIKey.user_id == user
        )
    )

    # ------------------------------------------------------
    # Status Filter
    # ------------------------------------------------------

    if status != "all":

        validate_status(status)

        query = query.filter(
            APIKey.status == status
        )

    keys = (
        query
        .order_by(
            APIKey.priority.desc(),
            APIKey.provider.asc()
        )
        .all()
    )

    return [
        build_key_response(key)
        for key in keys
    ]
           

# ==========================================================
# UPDATE API KEY
# ==========================================================

@router.patch("/{key_id}", response_model=KeyResponse)
def update_key(
    key_id: str,
    request: UpdateKeyRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    key = (
        db.query(APIKey)
        .options(
            selectinload(APIKey.models)
        )
        .filter(
            APIKey.key_id == key_id,
            APIKey.user_id == user
        )
        .first()
    )

    if key is None:

        raise HTTPException(
            status_code=404,
            detail="API key not found."
        )

    if (
        request.priority is None
        and request.limit is None
        and request.status is None
    ):

        raise HTTPException(
            status_code=400,
            detail="No fields provided for update."
        )

    # ------------------------------------------------------
    # Priority
    # ------------------------------------------------------

    if request.priority is not None:

        key.priority = request.priority

    # ------------------------------------------------------
    # Usage Limit
    # ------------------------------------------------------

    if request.limit is not None:

        key.limit = request.limit

    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    if request.status is not None:

        validate_status(request.status)

        key.status = request.status

        # Update all child models
        for model in key.models:

            model.status = request.status

    # ------------------------------------------------------
    # Commit
    # ------------------------------------------------------

    try:

        db.commit()

        db.refresh(key)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to update API key."
        )

    return build_key_response(key)

    
# ==========================================================
# DELETE API KEY
# ==========================================================

@router.delete("/{key_id}", response_model=MessageResponse)
def delete_key(
    key_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    key = (
        db.query(APIKey)
        .filter(
            APIKey.key_id == key_id,
            APIKey.user_id == user
        )
        .first()
    )

    if key is None:

        raise HTTPException(
            status_code=404,
            detail="API key not found."
        )

    try:

        db.delete(key)

        db.commit()

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to delete API key."
        )

    return MessageResponse(
        message="API key deleted successfully."
    )