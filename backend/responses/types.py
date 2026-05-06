from pydantic import BaseModel
from typing import Optional
from backend.types import FileRequest
from backend.router.types import RouterSuggestResponse, Suggestion

class ResponseFile(FileRequest):
    def __init__(self, meeting_id, timestamp, path="backend/responses/files/log.txt"):
        super().__init__(path=path,meeting_id=meeting_id,timestamp=timestamp)

class LoggedResponse(RouterSuggestResponse):
    transcript_window: str