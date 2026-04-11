import { AppServer, AppSession, ViewType } from '@mentra/sdk';
import {RouterSuggestRequest, RouterSuggestResponse, Suggestion, TranscriptFile, TranscriptRequest, TranscriptSnippet} from './types.ts';

const PACKAGE_NAME = process.env.PACKAGE_NAME ?? (() => { throw new Error('PACKAGE_NAME is not set in .env file'); })();
const MENTRAOS_API_KEY = process.env.MENTRAOS_API_KEY ?? (() => { throw new Error('MENTRAOS_API_KEY is not set in .env file'); })();
const PORT = parseInt(process.env.PORT || '3000');
const API_URL = "http://localhost:8000";

const TRANSCRIPT_FILE_PATH = undefined;

async function initTranscriptFile(meeting_id: string, path?: string): Promise<Object>{
  const headers: Headers = new Headers();
  headers.append("Content-Type", "application/json");
  let body: BodyInit = JSON.stringify(new TranscriptFile(meeting_id, new Date().toLocaleTimeString(),path));
  const api_query: RequestInfo = new Request(API_URL+'/api/v1/transcript/init', {method: 'POST',headers: headers,body: body});
  let res = await fetch(api_query); return await res.json();
}

async function streamTranscript(meeting_id:string, snippet: string): Promise<Object>{
  const headers: Headers = new Headers();
  headers.append("Content-Type", "application/json");
  const body: BodyInit = JSON.stringify(new TranscriptSnippet(snippet,meeting_id,new Date().toLocaleTimeString()));
  const api_query: RequestInfo = new Request(API_URL+'/api/v1/transcript/update', {method: 'POST',headers: headers,body: body});
  let res = await fetch(api_query); return await res.json();
}

async function deleteTranscript(): Promise<void>{
  const api_query: RequestInfo = new Request(API_URL+'/api/v1/transcript/', {method: 'DELETE'});
  await fetch(api_query);
}

async function getSuggestion(meeting_id: string, no_record_mode: boolean, top_k_context?: number): Promise<RouterSuggestResponse | void> {
  const headers: Headers = new Headers();
  headers.append("Content-Type", "application/json");
  const body: BodyInit = JSON.stringify(new RouterSuggestRequest(meeting_id,no_record_mode,top_k_context));
  console.log(body);
  const api_query: RequestInfo = new Request(API_URL+'/api/v1/suggest', {method: 'POST',headers: headers,body: body});
  let query_res : RouterSuggestResponse = new RouterSuggestResponse();
  console.log(api_query);
  let res = await fetch(api_query);res = await res.json();
  console.log(res);
  Object.assign(query_res, res);
  console.log(query_res);
  return query_res;
}

class LaylaCopilotApp extends AppServer {
  NO_RECORD_MODE: boolean;
  top_k_context?: number;
  constructor() {
    super({
      packageName: PACKAGE_NAME,
      apiKey: MENTRAOS_API_KEY,
      port: PORT,
    });
    this.NO_RECORD_MODE = false;
    this.top_k_context = 5;
  }

  protected async onSession(session: AppSession, sessionId: string, userId: string): Promise<void> {
    // Show welcome message
    session.layouts.showTextWall("Layla is ready");
    await initTranscriptFile(sessionId, TRANSCRIPT_FILE_PATH);
    // Handle real-time transcription
    // requires microphone permission to be set in the developer console

    session.events.onTranscription(async (data) => {
      if (data.isFinal) {
        // const suggestion_query = new RouterSuggestRequest(sessionId, data.text, this.no_record_mode, this.top_k_context);
        await streamTranscript(sessionId,data.text);
        let query = await getSuggestion(sessionId,this.NO_RECORD_MODE,this.top_k_context);
        console.log(query);
        session.layouts.showTextWall("Transcript: "+data.text+"\nSuggestion: "+query!.suggestion!.action);

      }
    })

    session.events.onGlassesBattery((data) => {
      console.log('Glasses battery:', data);
    })
  }
  protected async onStop(sessionId: string, userId: string, reason: string): Promise<void> {
    if(this.NO_RECORD_MODE){
      await deleteTranscript();
    }
  }
}

// Start the server
// DEV CONSOLE URL: https://console.mentra.glass/
// Get your webhook URL from ngrok (or whatever public URL you have)
const app = new LaylaCopilotApp();

app.start().catch(console.error);