from google import genai
from backend.router.adapter import AdapterResponse

class GeminiAdapter:
    def __init__(self):
        self.model_name = "gemini-3-flash-preview"
        self.client = genai.Client()

    def name(self) -> str:
        return self.model_name

    def generate_response(self, prompt: str) -> AdapterResponse:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": AdapterResponse.model_json_schema()
            }
        )
        result = AdapterResponse.model_validate_json(response.text) # FIXME: this can technically fail
        return result
