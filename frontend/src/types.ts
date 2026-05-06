import { assert } from "console";

export class ObservabilityMeta {
    request_id?: string;
    meeting_id?: string;
    latency_ms?: number;
    model_provider?: string;
    retrieval_hit_count?: number;
    timestamp?: string;
    constructor (request_id?: string, meeting_id?: string, latency_ms?: number, model_provider?: string, retrieval_hit_count?: number, timestamp?: string) {
        this.request_id = request_id;
        this.meeting_id = meeting_id;
        this.latency_ms = latency_ms;
        this.model_provider = model_provider;
        this.retrieval_hit_count = retrieval_hit_count;
        this.timestamp = timestamp;
    }
}
export class Citation {
    source_doc_id: string;
    snippet_id: string;
    start_char?: number;
    end_char?: number;
    constructor (source_doc_id: string, snippet_id: string,start_char?: number, end_char?: number){
        this.source_doc_id=source_doc_id;
        this.snippet_id=snippet_id;
        this.start_char=start_char;
        this.end_char=end_char;
    }
}
export class Suggestion{
    suggestion_id: string;
    response: string;
    rationale: string;
    confidence: number;
    citations: Citation[];
    latency_ms: number;
    constructor (suggestion_id: string,response: string,rationale: string,confidence: number,citations: Citation[],latency_ms: number){
        assert(confidence>=0.0&&confidence<=1.0);
        this.suggestion_id=suggestion_id;
        this.response=response;
        this.rationale=rationale;
        this.confidence=confidence;
        this.citations=citations;
        this.latency_ms=latency_ms;
    }
}
export class RouterSuggestRequest {
    meeting_id: string;
    // transcript_window: string;
    no_record_mode: boolean;
    top_k_context?: number;
    constructor (meeting_id: string, no_record_mode: boolean, top_k_context?: number) {
        this.meeting_id = meeting_id;
        // this.transcript_window = transcript_window;
        this.no_record_mode = no_record_mode;
        this.top_k_context = top_k_context;
    }
}
export class RouterSuggestResponse extends ObservabilityMeta {
    suggestion?: Suggestion;
    constructor(request_id?: string, meeting_id?: string, latency_ms?: number, model_provider?: string, retrieval_hit_count?: number, timestamp?: string, suggestion?: Suggestion){
        super(request_id, meeting_id, latency_ms, model_provider, retrieval_hit_count, timestamp);
        this.suggestion=suggestion;
    }
}

// Transcription streaming
class FileRequest {
    path: string;
    meeting_id: string;
    timestamp: string;
    constructor(path: string,meeting_id: string,timestamp: string){
        this.path=path;this.meeting_id=meeting_id;this.timestamp=timestamp;
    }
}
export class TranscriptFile extends FileRequest{
    constructor(meeting_id: string,timestamp: string,path?: string){
        if(path !== null && path !== undefined){
            super(path,meeting_id,timestamp);
        }
        else{
            super("backend/transcript/files/transcript.txt",meeting_id,timestamp);
        }
    }
}
export class TranscriptSnippet {
    snippet: string;
    meeting_id: string;
    timestamp: string;
    constructor(snippet: string,meeting_id: string,timestamp: string){
        this.meeting_id=meeting_id;this.snippet=snippet;this.timestamp=timestamp;
    }
}

export class TranscriptRequest {
    request_id: string;
    meeting_id: string;
    timestamp: string;
    length?: number;
    constructor(request_id: string,meeting_id: string,timestamp: string,length?: number){
        this.meeting_id=meeting_id;this.request_id=request_id;this.timestamp=timestamp;this.length=length;
    }
}

// Response log
export class ResponseFile extends FileRequest{
    constructor(meeting_id: string,timestamp: string,path?: string){
        if(path !== null && path !== undefined){
            super(path,meeting_id,timestamp);
        }
        else{
            super("backend/responses/files/log.txt",meeting_id,timestamp);
        }
    }
}
export class LoggedResponse extends RouterSuggestResponse {
    transcript_window: string;
    constructor(transcript_window: string, request_id?: string, meeting_id?: string, latency_ms?: number, model_provider?: string, retrieval_hit_count?: number, timestamp?: string, suggestion?: Suggestion){
        super(request_id, meeting_id, latency_ms, model_provider, retrieval_hit_count, timestamp);
        this.suggestion=suggestion;
        this.transcript_window=transcript_window;
    }
}