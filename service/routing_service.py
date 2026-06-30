import logging

from core.config import settings
from core.ml_router import ml_router, RouterPrediction
from core.routing_config import ROUTING_MAPPING

from schema.routing_schema import RoutingRequirements

from core.exceptions import RouterException


logger = logging.getLogger(__name__)


class RoutingService:
    """
    Converts a user prompt into RoutingRequirements
    using the ML Router.
    """

    @classmethod
    def analyze(
        cls,
        prompt: str
    ) -> RoutingRequirements:

        prediction = cls._predict(prompt)

        return cls._build_requirements(
            prediction
        )

    # ======================================================
    # PRIVATE
    # ======================================================

    @staticmethod
    def _predict(
        prompt: str
    ) -> RouterPrediction:

        try:

            return ml_router.classify(prompt)

        except Exception as e:

            raise RouterException(
                "Routing prediction failed."
            ) from e

    @staticmethod
    def _build_requirements(
        prediction: RouterPrediction
    ) -> RoutingRequirements:

        requirements = RoutingRequirements()

        for label, score in zip(
            prediction.labels,
            prediction.scores
        ):

            if score < settings.ROUTER_THRESHOLD:
                continue

            mapping = ROUTING_MAPPING.get(label)

            if mapping is None:

                logger.warning(
                    "No routing mapping found for '%s'",
                    label
                )

                continue
            for field, value in mapping.items():
                if not hasattr(requirements, field):
                    logger.warning(
                        "Unknown routing field '%s'",
                        field
                    )
                    continue

                setattr(
                    requirements,
                    field,
                    value
                )

        logger.info(

            "Routing Result | label=%s | confidence=%.2f | latency=%.2f ms",

            prediction.top_label,

            prediction.confidence,

            prediction.inference_time_ms
        )

        return requirements