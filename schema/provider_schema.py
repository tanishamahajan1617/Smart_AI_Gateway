from typing import Optional, Dict, Any

from pydantic import BaseModel


# ==========================================================
# TOKEN USAGE
# ==========================================================

class Usage(BaseModel):

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int

    total_cost_usd: float = 0.0


# ==========================================================
# PROVIDER RESPONSE
# ==========================================================

class ProviderResponse(BaseModel):

    content: str

    provider: str

    model: str

    latency_ms: float

    usage: Usage

    metadata: Optional[Dict[str, Any]] = None