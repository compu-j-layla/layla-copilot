from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime
from httpx import AsyncClient
from backend.router.gemini_adapter import GeminiAdapter
from backend.types import ObservabilityMeta, Citation
import asyncio

TRANSCRIPT_WINDOWS_TRUCATE_LENGTH = 1000
RAG_BASE_URL = "http://localhost:8000"
RAG_QUERY_ENDPOINT = "/api/v1/rag/query"
RAG_TRANSCRIPT_WINDOW_SLICE = 300
RAG_DEFAULT_TOP_K = 5


class Suggestion(BaseModel):
    suggestion_id: str
    action: str
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

rag_query_client = AsyncClient(base_url=RAG_BASE_URL)
llm_adapter = GeminiAdapter() # FIXME: make this configurable

def router_suggest(meeting_id: str, transcript_window: str, no_record_mode: bool, top_k_context: Optional[int]):
    try:
        request_id = str(uuid.uuid4())
        suggestion_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # TODO: respect no_record_mode privacy constraints

        truncated_transcript = transcript_window[-TRANSCRIPT_WINDOWS_TRUCATE_LENGTH:]
        rag_context = ""
        if should_use_rag(truncated_transcript):
            rag_query_request = {
                'meeting_id': meeting_id,
                'query': truncated_transcript[-RAG_TRANSCRIPT_WINDOW_SLICE:],
                'top_k': top_k_context or RAG_DEFAULT_TOP_K
            }
            rag_context = asyncio.run(rag_query_client.post(RAG_QUERY_ENDPOINT, json=rag_query_request))

        prompt = """
        You are an AI copilot assistant for meetings. Based on the following transcript window and retrieved context,
        suggest one action that the user can take, along with a rationale and confidence score. The action should be
        specific and actionable. The rationale should explain why this action is relevant to the transcript. The confidence
        score should be between 0 and 1, indicating how confident you are in the suggestion.
        
        If no relevant action can be suggested, return an empty action. Be concise in your response. Base your suggestion
        only on the provided transcript window and the retrieved context, without making any assumptions about the meeting
        or its participants, or drawing on any external sources of knowledge.

        If you include information from the retrieved context in your rationale, please include citations to the source
        documents. Each citation should reference a source document ID, snippet ID from the retrieved context, and, if possible,
        the character offsets of the relevant information in the source document.

        Here is the transcript window:
        {transcript_window}

        Here is the provided context:
        {rag_context}
        """

        llm_response = llm_adapter.generate_response(prompt.format(transcript_window=truncated_transcript, rag_context=rag_context))

        end_time = datetime.now()
        latency_ms = int((end_time - start_time).total_seconds() * 1000)
        
        suggestion = Suggestion(
            suggestion_id=suggestion_id,
            action=llm_response.action,
            rationale=llm_response.rationale,
            confidence=llm_response.confidence,
            citations=llm_response.citations,
            latency_ms=latency_ms,
        )
        
        return RouterSuggestResponse(
            request_id=request_id,
            meeting_id=meeting_id,
            latency_ms=latency_ms,
            model_provider=llm_adapter.name(),
            retrieval_hit_count=0,
            timestamp=end_time.isoformat(),
            suggestion=suggestion,
        )
    
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def should_use_rag(transcript_window: str) -> bool:
    rag_keywords = [ "document", "report", "email", "presentation", "meeting", "deadline", "budget" ]
    return any(keyword in transcript_window.lower() for keyword in rag_keywords)
