from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime
from httpx import AsyncClient
from backend.router.gemini_adapter import GeminiAdapter
from backend.types import ObservabilityMeta, Citation
import asyncio

import logging
from backend.transcript.types import *

TRANSCRIPT_TRUNCATE_LENGTH = 1000
TRANSCRIPT_WINDOWS_TRUNCATE_LENGTH = 30
TRANSCRIPT_WINDOWS_SHORTEST_LENGTH = 20
RAG_BASE_URL = "http://localhost:8000"
RAG_QUERY_ENDPOINT = "/api/v1/rag/query"
RAG_TRANSCRIPT_WINDOW_SLICE = 300
RAG_DEFAULT_TOP_K = 5

DEMO_MODE = True

TRANSCRIPT_BASE_URL = "http://localhost:8000" # TO-DO: host the API non-locally
TRANSCRIPT_QUERY_ENDPOINT = "/api/v1/transcript/"

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

rag_query_client = AsyncClient(base_url=RAG_BASE_URL)
llm_adapter = GeminiAdapter() # FIXME: make this configurable

transcript_query_client = AsyncClient(base_url=TRANSCRIPT_BASE_URL) 

# debug log
logger = logging.getLogger("uvicorn.error")

async def router_suggest(meeting_id: str, no_record_mode: bool, top_k_context: Optional[int]):
    try:
        request_id = str(uuid.uuid4())
        suggestion_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # get transcript window from transcript file
        transcript_window_request = {
            'meeting_id': meeting_id,
            'request_id': request_id,
            'timestamp': str(start_time),
            'length': TRANSCRIPT_TRUNCATE_LENGTH
        }
        transcript_window_response = await transcript_query_client.post(TRANSCRIPT_QUERY_ENDPOINT, json=transcript_window_request)
        truncated_transcript = transcript_window_response.text
        __lineskips_to_delete = 2
        __pos = 0
        while __pos < (len(truncated_transcript) - 1) and __lineskips_to_delete > 0:
            if(truncated_transcript[__pos]=='\\' and truncated_transcript[__pos+1]=='n'):
                __lineskips_to_delete -= 1
                __pos+=1
            __pos += 1
        truncated_transcript = truncated_transcript[__pos:-1]
        logger.debug(truncated_transcript)

        if len(truncated_transcript.split()) < TRANSCRIPT_WINDOWS_SHORTEST_LENGTH:
            # context is too short, wait until more context is given
            end_time = datetime.now()
            latency_ms = int((end_time - start_time).total_seconds() * 1000)
            return RouterSuggestResponse(
                request_id=request_id,
                meeting_id=meeting_id,
                latency_ms=latency_ms,
                model_provider=llm_adapter.name(),
                retrieval_hit_count=0,
                timestamp=end_time.isoformat(),
                suggestion=Suggestion(
                    suggestion_id=suggestion_id,
                    response="awaiting more context.",
                    rationale="meeting has not progressed enough for a response",
                    confidence="1.0",
                    citations=[],
                    latency_ms=latency_ms,
                )
            )

        # TODO: respect no_record_mode privacy constraints

        transcript_window = " ".join((truncated_transcript.split()[-TRANSCRIPT_WINDOWS_TRUNCATE_LENGTH:]))
        rag_context = ""
        if should_use_rag(truncated_transcript):
            rag_query_request = {
                'meeting_id': meeting_id,
                'query': truncated_transcript[-RAG_TRANSCRIPT_WINDOW_SLICE:],
                'top_k': top_k_context or RAG_DEFAULT_TOP_K
            }
            rag_query = await rag_query_client.post(RAG_QUERY_ENDPOINT, json=rag_query_request)
            
            rag_context_list = rag_query.json()
            rag_context = ""
            
            for snippet in rag_context_list:
                rag_context += "- snippet: <begin>" + snippet["text"] + "<end>"
                rag_context += "\n"
            logger.debug(type(rag_context))
            logger.debug(rag_context)

        # FIXME: Parse RAG context into chunks of text instead of a json format array straight from the response
        # FIXME: Adapt the prompt for word limits / to produce actually useful results
        prompt = """
        You are an AI copilot assistant for meetings. Based on the following transcript window, the full transcript, and retrieved context,
        provide information or suggestions that may be relevant, along with a rationale and confidence score. The response should be concise, in 15 words and specific. The rationale should explain why the returned information / suggestions are relevant to the transcript. The confidence score should be between 0 and 1, indicating how confident you are in the suggestion.
        
        If no relevant information or suggestion can be given, recap the provided context in 15 words. Be very concise in your response, keeping it within 15 words. Base your suggestion
        only on the provided transcript window and the retrieved context, without making any assumptions about the meeting
        or its participants, or drawing on any external sources of knowledge.

        If you include information from the retrieved context in your rationale, please include citations to the source
        documents. Each citation should reference a source document ID, snippet ID from the retrieved context, and, if possible,
        the character offsets of the relevant information in the source document.

        Here is the transcript window:
        {transcript_window}

        Here is the full transcript:
        {full_transcript}

        Here is a list of possible relevant snippets:
        {rag_context}
        """
        formatted_prompt = prompt.format(transcript_window=transcript_window,full_transcript=truncated_transcript, rag_context=rag_context)
        logger.debug(formatted_prompt)
        llm_response = llm_adapter.generate_response(formatted_prompt)

        end_time = datetime.now()
        latency_ms = int((end_time - start_time).total_seconds() * 1000)
        
        suggestion = Suggestion(
            suggestion_id=suggestion_id,
            response=llm_response.response,
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

# TODO: change the conditions of checking in RAG (maybe have it be always on?)
def should_use_rag(transcript_window: str) -> bool:
    rag_keywords = [ "document", "report", "email", "presentation", "meeting", "deadline", "budget", "context"]
    return DEMO_MODE or any(keyword in transcript_window.lower() for keyword in rag_keywords)
