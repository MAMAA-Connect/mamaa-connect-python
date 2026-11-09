import os
from google import genai
from google.genai import types
from mamaa_connect.core import BaseAIAdapter, Provider, UnifiedRequest, UnifiedResponse


class GoogleGeminiAdapter(BaseAIAdapter):
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.client = genai.Client(api_key=self.api_key)

    @property
    def provider_name(self) -> Provider:
        return Provider.GOOGLE

    def generate(self, request: UnifiedRequest) -> UnifiedResponse:
        prompt = "\n".join([f"{m.role}: {m.content}" for m in request.messages])
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
            ),
        )
        return UnifiedResponse(
            provider=self.provider_name,
            model=self.model,
            content=response.text or "",
            usage={"total_tokens": getattr(response.usage_metadata, "total_token_count", 0)},
        )
