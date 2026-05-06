from pydantic import BaseModel
from typing import Optional

class ObservabilityMeta(BaseModel):
    request_id: str
    meeting_id: str
    latency_ms: int
    model_provider: str
    retrieval_hit_count: int
    timestamp: str

class Citation(BaseModel):
    source_doc_id: str
    snippet_id: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None

class FileRequest(BaseModel):
    path: str
    meeting_id: str
    timestamp: str
