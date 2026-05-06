from pydantic import BaseModel, Field
from backend.types import Citation

class AdapterResponse(BaseModel):
    response: str
    rationale: str
    confidence: float = Field(ge=0, le=1)
    citations: list[Citation]
