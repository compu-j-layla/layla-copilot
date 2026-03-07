from fastapi import FastAPI
from backend.rag.ingest import ingest_document
from backend.rag.retrieval import retrieve
from pydantic import BaseModel

app = FastAPI()

class DocumentIngestRequest(BaseModel):

    doc_id: str
    source_type: str
    source_path: str
    tags: list[str]



class RagQueryRequest(BaseModel):

    meeting_id: str
    query: str
    top_k: int


@app.post('/api/v1/rag/documents')
def ingest(request: DocumentIngestRequest):
    return ingest_document(request.doc_id, request.source_type, request.source_path, request.tags)


@app.post('/api/v1/rag/query')
def query(request: RagQueryRequest):
    return retrieve(request.query, request.top_k)
