from fastapi import FastAPI
from backend.rag.ingest import ingest_document
from backend.rag.retrieval import retrieve
from backend.router.router import router_suggest
from pydantic import BaseModel
from typing import Optional
from backend.transcript.types import TranscriptSnippet, TranscriptFile, TranscriptRequest
from backend.transcript.stream import *
from backend.responses.stream import *
from backend.responses.types import ResponseFile
import uvicorn
import logging
import os

app = FastAPI()
# debug log
logger = logging.getLogger("uvicorn.error")

class DocumentIngestRequest(BaseModel):
    doc_id: str
    source_type: str
    source_path: str
    tags: list[str]



class RagQueryRequest(BaseModel):
    meeting_id: str
    query: str
    top_k: int


class RouterSuggestRequest(BaseModel):
    meeting_id: str
    # transcript_window: str
    no_record_mode: bool
    top_k_context: Optional[int]


@app.post('/api/v1/rag/documents')
async def ingest(request: DocumentIngestRequest):
    return ingest_document(request.doc_id, request.source_type, request.source_path, request.tags)


@app.post('/api/v1/rag/query')
async def query(request: RagQueryRequest):
    return retrieve(request.query, request.top_k)


@app.post('/api/v1/suggest')
async def suggest(request: RouterSuggestRequest):
    return await router_suggest(request.meeting_id, request.no_record_mode, request.top_k_context)

# audio stream
@app.post('/api/v1/stream/audio')
async def stream():
    # TODO: implement uploading / appending to audio recording of the meeting
    # TODO: find a way to stream / record audio whilst using the MentraOS transcript function (perhaps switch to processing each audio chunk with another speech recognition model? or separate into recording / suggestion / assist modes)
    pass

# transcripts

# TRANSCRIPT_PATH = "/files/transcript.txt"
# initialise transcript context
@app.post('/api/v1/transcript/init', status_code=201) # 201 to indicate file creation, might be unnecessary
async def transcript_init(request: TranscriptFile):
    return init_file(request.meeting_id, request.timestamp, request.path)

@app.post('/api/v1/transcript/update')
async def transcript_update(request: TranscriptSnippet):
    return update_file(request.snippet)

@app.post('/api/v1/transcript/')
async def get_transcript(request: TranscriptRequest):
    return read_transcript(request.length)

@app.delete('/api/v1/transcript')
async def delete_file():
    delete_transcript()

# response logs
@app.post('/api/v1/responses/init', status_code=201)
# 201 to indicate file creation, might be unnecessary
async def responses_init(request: ResponseFile):
    return init_log(request.meeting_id, request.timestamp, request.path)

@app.post('/api/v1/responses/update')
async def responses_update(request: LoggedResponse):
    logger.debug(request)
    return update_log(request)

@app.delete('/api/v1/responses')
async def delete_responses():
    delete_log()