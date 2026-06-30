from typing import List, Tuple

from models.api_key_models import APIKeyModel
from schema.routing_schema import RoutingRequirements


class ScoringEngine:

    # ======================================================
    # WEIGHTS
    # ======================================================

    PRIORITY_WEIGHT = 20

    QUALITY_WEIGHT = 10

    SPEED_WEIGHT = 8

    PRICE_WEIGHT = 8

    CONTEXT_WEIGHT = 5

    LATENCY_WEIGHT = 5

    PREFERRED_PROVIDER_BONUS = 25

    OPEN_SOURCE_BONUS = 20

    OPEN_SOURCE_PENALTY = -100

    # ======================================================

    @classmethod
    def calculate_score(
        cls,
        candidate: APIKeyModel,
        requirements: RoutingRequirements
    ) -> Tuple[float, List[str]]:

        score = 0.0

        reasons = []

        key = candidate.api_key

        # --------------------------------------------------
        # User Priority
        # --------------------------------------------------

        priority_score = (
            key.priority * cls.PRIORITY_WEIGHT
        )

        score += priority_score

        reasons.append(
            f"Priority ({key.priority})"
        )

        # --------------------------------------------------
        # Reasoning Capability
        # --------------------------------------------------

        if requirements.reasoning:

            quality = candidate.quality_rating or 0

            quality_score = (
                quality * cls.QUALITY_WEIGHT
            )

            score += quality_score

            reasons.append(
                f"Quality Rating ({quality})"
            )

        # --------------------------------------------------
        # Speed Requirement
        # --------------------------------------------------

        if requirements.fast_response:

            speed = candidate.speed_rating or 0

            speed_score = (
                speed * cls.SPEED_WEIGHT
            )

            score += speed_score

            reasons.append(
                f"Speed Rating ({speed})"
            )

            if candidate.latency:

                latency_bonus = max(
                    0,
                    cls.LATENCY_WEIGHT - candidate.latency
                )

                score += latency_bonus

                reasons.append(
                    f"Latency ({candidate.latency:.2f}s)"
                )

        # --------------------------------------------------
        # Long Context
        # --------------------------------------------------

        if requirements.long_context:

            context = (
                candidate.context_window or 0
            )

            context_score = (
                context / 100000
            ) * cls.CONTEXT_WEIGHT

            score += context_score

            reasons.append(
                f"Context ({context})"
            )

        # --------------------------------------------------
        # Low Cost
        # --------------------------------------------------

        if requirements.low_cost:

            price = (
                candidate.price_rating or 0
            )

            price_score = (
                price * cls.PRICE_WEIGHT
            )

            score += price_score

            reasons.append(
                f"Price Rating ({price})"
            )

        # --------------------------------------------------
        # Open Source
        # --------------------------------------------------

        if requirements.open_source_only:

            if candidate.open_source:

                score += cls.OPEN_SOURCE_BONUS

                reasons.append(
                    "Open Source"
                )

            else:

                score += cls.OPEN_SOURCE_PENALTY

                reasons.append(
                    "Not Open Source"
                )

        # --------------------------------------------------
        # Preferred Provider
        # --------------------------------------------------

        if (
            requirements.preferred_provider
            and key.provider.lower()
            == requirements.preferred_provider.lower()
        ):

            score += cls.PREFERRED_PROVIDER_BONUS

            reasons.append(
                "Preferred Provider"
            )

        return score, reasons