from pydantic import BaseModel, Field
from typing import Optional
from backend.types import ObservabilityMeta, Citation

class Suggestion(BaseModel):
    suggestion_id: str
    response: str
    rationale: str
    confidence: float = Field(ge=0, le=1)
    citations: list[Citation]
    latency_ms: int


class RouterSuggestResponse(ObservabilityMeta):
    suggestion: Suggestion


class ErrorBody(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


class ErrorEnvelope(BaseModel):
    error: ErrorBody
    request_id: str
    timestamp: str