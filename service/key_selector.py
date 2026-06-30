from typing import List

from fastapi import HTTPException

from sqlalchemy.orm import (
    Session,
    selectinload
)

from models.api_key import APIKey
from models.api_key_models import APIKeyModel

from schema.routing_schema import (
    RankedKey,
    RoutingRequirements
)

from service.scoring import ScoringEngine

from core.exceptions import (
    NoActiveAPIKeysError,
    NoUsableAPIKeysError
)

class KeySelector:

    @classmethod
    def select_keys(
        cls,
        db: Session,
        user_id: str,
        requirements: RoutingRequirements
    ) -> List[RankedKey]:

        # ------------------------------------
        # Load Candidates
        # ------------------------------------

        candidates = cls._load_candidates(
            db,
            user_id
        )

        if not candidates:

            raise HTTPException(
                status_code=404,
                detail="No API keys found."
            )

        # ------------------------------------
        # Filters
        # ------------------------------------

        candidates = cls._filter_active(
            candidates
        )

        if not candidates:

            raise NoActiveAPIKeysError()

        candidates = cls._filter_token_limit(
            candidates
        )

        candidates = cls._filter_health(
            candidates
        )

        candidates = cls._filter_rate_limit(
            candidates
        )

        candidates = cls._filter_provider(
            candidates,
            requirements
        )

        candidates = cls._filter_capability(
            candidates,
            requirements
        )

        if not candidates:

            raise NoUsableAPIKeysError()

        # ------------------------------------
        # Ranking
        # ------------------------------------

        return cls._rank_candidates(
            candidates,
            requirements
        )

    # ====================================================
    # DATABASE
    # ====================================================

    @staticmethod
    def _load_candidates(
        db: Session,
        user_id: str
    ) -> List[APIKeyModel]:

        return (

            db.query(APIKeyModel)

            .join(APIKey)

            .options(
                selectinload(
                    APIKeyModel.api_key
                )
            )

            .filter(
                APIKey.user_id == user_id
            )

            .all()

        )

    # ====================================================
    # FILTERS
    # ====================================================

    @staticmethod
    def _filter_active(
        candidates: List[APIKeyModel]
    ) -> List[APIKeyModel]:

        return [

            candidate

            for candidate in candidates

            if (

                candidate.status == "active"

                and

                candidate.api_key.status == "active"

            )

        ]

    @staticmethod
    def _filter_token_limit(
        candidates: List[APIKeyModel]
    ) -> List[APIKeyModel]:

        usable = []

        for candidate in candidates:

            key = candidate.api_key

            if key.limit is None:

                usable.append(candidate)

            elif candidate.tokens_used < key.limit:

                usable.append(candidate)

        return usable

    @staticmethod
    def _filter_health(
        candidates: List[APIKeyModel]
    ) -> List[APIKeyModel]:

        return candidates

    @staticmethod
    def _filter_rate_limit(
        candidates: List[APIKeyModel]
    ) -> List[APIKeyModel]:

        return candidates

    @staticmethod
    def _filter_provider(
        candidates: List[APIKeyModel],
        requirements: RoutingRequirements
    ) -> List[APIKeyModel]:

        if not requirements.preferred_provider:

            return candidates

        return [

            candidate

            for candidate in candidates

            if candidate.api_key.provider.lower()
            == requirements.preferred_provider.lower()

        ]

    @staticmethod
    def _filter_capability(
        candidates: List[APIKeyModel],
        requirements: RoutingRequirements
    ) -> List[APIKeyModel]:

        return candidates

    # ====================================================
    # RANKING
    # ====================================================

    @staticmethod
    def _rank_candidates(
        candidates: List[APIKeyModel],
        requirements: RoutingRequirements
    ) -> List[RankedKey]:

        ranked = []

        for candidate in candidates:

            score, reasons = (
                ScoringEngine.calculate_score(
                    candidate,
                    requirements
                )
            )

            ranked.append(

                RankedKey(

                    key=candidate.api_key,

                    model=candidate,

                    score=score,

                    reasons=reasons

                )

            )

        ranked.sort(

    key=lambda x: (

        x.score,

        x.key.priority,

        -(x.model.failure_count or 0),

        -(x.model.latency or float("inf"))

    ),

    reverse=True

)

        return ranked