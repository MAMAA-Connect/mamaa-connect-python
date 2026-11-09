import os
from openai import OpenAI
from mamaa_connect.core import BaseAIAdapter, Provider, UnifiedRequest, UnifiedResponse


class MetaLlamaAdapter(BaseAIAdapter):
    """Connects to Meta Llama models hosted on Llama API, Groq, Together, or self-hosted vLLM."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://llama.com",
        model: str = "Llama-3.3-70B-Instruct",
    ):
        self.model = model
        self.client = OpenAI(
            api_key=api_key or os.getenv("META_LLAMA_API_KEY", ""),
            base_url=base_url,
        )

    @property
    def provider_name(self) -> Provider:
        return Provider.META

    def generate(self, request: UnifiedRequest) -> UnifiedResponse:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        return UnifiedResponse(
            provider=self.provider_name,
            model=self.model,
            content=response.choices[0].message.content or "",
        )
