from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.transcript.types import TranscriptSnippet, TranscriptFile, TranscriptRequest
import uvicorn
import logging
import os

TRANSCRIPT_PATH = "backend/transcript/files/transcript.txt"

# debug log
logger = logging.getLogger("uvicorn.error")

def init_file(meeting_id,timestamp,filepath=None):
    global TRANSCRIPT_PATH
    if filepath is not None:
        TRANSCRIPT_PATH = filepath
    try:
        os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)
        with open(TRANSCRIPT_PATH, "w+") as transcriptFile:
            transcriptFile.write("Meeting ID: "+meeting_id+"\nTimestamp: "+timestamp+"\n")
        return {"transcript_file":TRANSCRIPT_PATH}
    except Exception as e:
        # TODO: change status code to indicate file creation failure
        raise HTTPException(status_code=500, detail=str(e))

def update_file(snippet):
    global TRANSCRIPT_PATH
    try:
        with open(TRANSCRIPT_PATH,"r"):
            # FIXME: find a better way to test if file exists
            pass
        with open(TRANSCRIPT_PATH, "a+") as transcriptFile:
            # logger.debug(msg=str(transcriptFile.read()))
            transcriptFile.write(snippet+" ")
        return {"transcript_file":TRANSCRIPT_PATH}
    except Exception as e:
        # TODO: change status code to indicate file open failure
        raise HTTPException(status_code=500, detail=str(e))
    
def read_transcript(limit=None):
    global TRANSCRIPT_PATH
    try:
        with open(TRANSCRIPT_PATH, "r") as transcriptFile:
            transcript = transcriptFile.read()
            if(limit is not None):
                transcript = transcript[-limit:]
            return transcript
    except Exception as e:
        # TODO: change status code to indicate file open failure
        raise HTTPException(status_code=404, detail=str(e))

def delete_transcript():
    global TRANSCRIPT_PATH
    try:
        os.remove(TRANSCRIPT_PATH)
    except Exception as e:
        # TODO: change status code to indicate file open failure
        raise HTTPException(status_code=404, detail=str(e))