from datetime import datetime, timezone

from sqlalchemy.orm import Session

from core.encrypt import decrypt_key
from core.secure_keys import mask_key

from models.api_key import APIKey
from models.api_key_models import APIKeyModel

from schema.key_schema import (
    KeyResponse,
    ModelResponse
)


# ======================================================
# RESPONSE MAPPER
# ======================================================

def build_key_response(
    key: APIKey
) -> KeyResponse:

    try:

        masked_key = mask_key(
            decrypt_key(key.api_key)
        )

    except Exception:

        masked_key = "********"

    models = []

    for model in key.models:

        models.append(

            ModelResponse(

                model_id=model.model_id,

                model=model.model,

                context_window=model.context_window,

                speed=model.speed,

                latency=model.latency,

                mmlu_score=model.mmlu_score,

                arena_score=model.arena_score,

                price_per_million_tokens=model.price_per_million_tokens,

                quality_rating=model.quality_rating,

                speed_rating=model.speed_rating,

                price_rating=model.price_rating,

                open_source=model.open_source,

                tokens_used=model.tokens_used,

                status=model.status

            )

        )

    return KeyResponse(

        key_id=key.key_id,

        provider=key.provider,

        api_key=masked_key,

        priority=key.priority,

        limit=key.limit,

        status=key.status,

        created_at=key.created_at,

        updated_at=key.updated_at,

        models=models

    )


# ======================================================
# KEY SERVICE
# ======================================================

class KeyService:

    @staticmethod
    def get_user_keys(
        db: Session,
        user_id: str
    ) -> list[APIKey]:

        return (

            db.query(APIKey)

            .filter(
                APIKey.user_id == user_id,
                APIKey.status == "active"
            )

            .order_by(
                APIKey.priority.desc()
            )

            .all()

        )

    # ======================================================
    # USAGE
    # ======================================================

    @staticmethod
    def update_usage(
        key: APIKey,
        model: APIKeyModel,
        tokens_used: int
    ) -> None:

        # API Key Usage (Billing)

        key.tokens_used += tokens_used

        # Model Usage (Analytics)

        model.tokens_used += tokens_used

        model.last_used_at = datetime.now(
            timezone.utc
        )

    # ======================================================
    # FAILURES
    # ======================================================

    @staticmethod
    def record_failure(
        model: APIKeyModel,
        error: str
    ) -> None:

        model.failure_count += 1

        model.last_error = error

    @staticmethod
    def reset_failure(
        model: APIKeyModel
    ) -> None:

        model.failure_count = 0

        model.last_error = None

    @staticmethod
    def increment_retry(
        model: APIKeyModel
    ) -> None:

        model.failure_count += 1

    # ======================================================
    # AVAILABILITY
    # ======================================================

    @staticmethod
    def is_available(
        model: APIKeyModel
    ) -> bool:

        key = model.api_key

        if key.status != "active":

            return False

        if model.status != "active":

            return False

        if (
            key.limit is not None
            and key.tokens_used >= key.limit
        ):

            return False

        return True

    @staticmethod
    def get_available_models(
        db: Session,
        user_id: str
    ) -> list[APIKeyModel]:

        available = []

        keys = KeyService.get_user_keys(
            db,
            user_id
        )

        for key in keys:

            for model in key.models:

                if KeyService.is_available(
                    model
                ):

                    available.append(model)

        return available