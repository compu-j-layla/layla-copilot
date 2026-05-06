from pydantic import BaseModel
from typing import Optional
from backend.types import FileRequest

class TranscriptFile(FileRequest):
    def __init__(self, meeting_id, timestamp, path="backend/transcript/files/transcript.txt"):
        super().__init__(path=path,meeting_id=meeting_id,timestamp=timestamp)

class TranscriptSnippet(BaseModel):
    snippet: str
    meeting_id: str
    timestamp: str

class TranscriptRequest(BaseModel):
    request_id: str
    meeting_id: str
    timestamp: str
    length: Optional[int] = None