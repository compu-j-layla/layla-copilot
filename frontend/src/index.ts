import { AppServer, AppSession, ViewType } from '@mentra/sdk';
import {RouterSuggestRequest, RouterSuggestResponse, Suggestion} from './types.ts';

const PACKAGE_NAME = process.env.PACKAGE_NAME ?? (() => { throw new Error('PACKAGE_NAME is not set in .env file'); })();
const MENTRAOS_API_KEY = process.env.MENTRAOS_API_KEY ?? (() => { throw new Error('MENTRAOS_API_KEY is not set in .env file'); })();
const PORT = parseInt(process.env.PORT || '3000');
const API_URL = "http://localhost:8000";

async function getSuggestion(request: RouterSuggestRequest): Promise<RouterSuggestResponse | void> {
  const headers: Headers = new Headers();
  headers.append("Content-Type", "application/json");
  const body: BodyInit = JSON.stringify(request);
  console.log(body);
  const api_query: RequestInfo = new Request(API_URL+'/api/v1/suggest', {
    method: 'POST',
    headers: headers,
    body: body
  });
  let query_res : RouterSuggestResponse = new RouterSuggestResponse();
  console.log(api_query);
  let res = await fetch(api_query);res = await res.json();
  console.log(res);
  Object.assign(query_res, res);
  console.log(query_res);
  return query_res;
}

class LaylaCopilotApp extends AppServer {
  no_record_mode: boolean;
  top_k_context?: number;
  constructor() {
    super({
      packageName: PACKAGE_NAME,
      apiKey: MENTRAOS_API_KEY,
      port: PORT,
    });
    this.no_record_mode = false;
    this.top_k_context = 5;
  }

  protected async onSession(session: AppSession, sessionId: string, userId: string): Promise<void> {
    // Show welcome message
    session.layouts.showTextWall("Layla is ready");

    // Handle real-time transcription
    // requires microphone permission to be set in the developer console
    session.events.onTranscription(async (data) => {
      if (data.isFinal) {
        const suggestion_query = new RouterSuggestRequest(sessionId, data.text, this.no_record_mode, this.top_k_context);
        let query = await getSuggestion(suggestion_query);
        console.log(query);
        session.layouts.showTextWall("Query: "+data.text+"\nAction: "+query!.suggestion!.action);
      }
    })

    session.events.onGlassesBattery((data) => {
      console.log('Glasses battery:', data);
    })
  }
}

// Start the server
// DEV CONSOLE URL: https://console.mentra.glass/
// Get your webhook URL from ngrok (or whatever public URL you have)
const app = new LaylaCopilotApp();

app.start().catch(console.error);