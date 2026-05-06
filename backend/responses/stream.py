from backend.router.types import RouterSuggestResponse, Suggestion
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.transcript.types import TranscriptSnippet, TranscriptFile, TranscriptRequest
from backend.types import ObservabilityMeta
from backend.responses.types import *
import uvicorn
import logging
import os

RESPONSE_LOG_PATH = "backend/responses/files/log.txt"

# debug log
logger = logging.getLogger("uvicorn.error")

def init_log(meeting_id,timestamp,filepath=None):
    global RESPONSE_LOG_PATH
    if filepath is not None:
        RESPONSE_LOG_PATH = filepath
    try:
        os.makedirs(os.path.dirname(RESPONSE_LOG_PATH), exist_ok=True)
        with open(RESPONSE_LOG_PATH, "w+") as responseLog:
            responseLog.write("<RESPONSE LOG>\nMeeting ID: "+meeting_id+"\nTimestamp: "+timestamp+"\n")
        return {"transcript_file":RESPONSE_LOG_PATH}
    except Exception as e:
        # TODO: change status code to indicate file creation failure
        raise HTTPException(status_code=500, detail=str(e))

def update_log(response: LoggedResponse):
    global RESPONSE_LOG_PATH
    try:
        with open(RESPONSE_LOG_PATH,"r"):
            # FIXME: find a better way to test if file exists
            pass
        logger.debug("hi, log file is ok")
        with open(RESPONSE_LOG_PATH, "a+") as responseLog:
            # logger.debug(msg=str(transcriptFile.read()))
            responseLog.write("*******\nTimestamp: "+response.timestamp+"\nRequest id: "+response.request_id+"\nTranscript Window: "+response.transcript_window+"\nResponse details:\n - Suggestion: "+response.suggestion.response+"\n - Rationale: "+response.suggestion.rationale+"\n - Confidence: "+str(response.suggestion.confidence)+"\n - Latency: "+str(response.suggestion.latency_ms)+"\n - Citations: "+"\n - - ".join(["source doc id:"+c.source_doc_id+"; snippet_id:"+c.snippet_id for c in response.suggestion.citations])+"\n********\n")
        return {"transcript_file":RESPONSE_LOG_PATH}
    except Exception as e:
        # TODO: change status code to indicate file open failure
        logger.debug(e)
        raise HTTPException(status_code=500, detail=str(e))

def delete_log():
    global RESPONSE_LOG_PATH
    try:
        os.remove(RESPONSE_LOG_PATH)
    except Exception as e:
        # TODO: change status code to indicate file open failure
        raise HTTPException(status_code=404, detail=str(e))