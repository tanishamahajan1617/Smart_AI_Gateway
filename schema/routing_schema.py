from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from models.api_key import APIKey
from models.api_key_models import APIKeyModel


@dataclass
class RankedKey:

    # Parent API Key
    key: APIKey

    # Selected Model
    model: APIKeyModel

    # Final routing score
    score: float

    # Why this candidate was selected
    reasons: list[str]


class RoutingRequirements(BaseModel):

    # Query characteristics
    reasoning: bool = False
    long_context: bool = False
    fast_response: bool = False
    low_cost: bool = False

    # Provider preference
    preferred_provider: Optional[str] = None

    # Constraints
    open_source_only: bool = False

    # Future
    multimodal: bool = False
    code_generation: bool = False
    json_output: bool = False
    streaming: bool = False