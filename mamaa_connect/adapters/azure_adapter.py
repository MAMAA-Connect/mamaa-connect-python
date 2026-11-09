import os
from openai import AzureOpenAI
from mamaa_connect.core import BaseAIAdapter, Provider, UnifiedRequest, UnifiedResponse


class AzureOpenAIAdapter(BaseAIAdapter):
    def __init__(
        self,
        endpoint: str | None = None,
        api_key: str | None = None,
        deployment_name: str = "gpt-4o",
        api_version: str = "2024-06-01",
    ):
        self.deployment_name = deployment_name
        self.client = AzureOpenAI(
            azure_endpoint=endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            api_key=api_key or os.getenv("AZURE_OPENAI_API_KEY", ""),
            api_version=api_version,
        )

    @property
    def provider_name(self) -> Provider:
        return Provider.AZURE

    def generate(self, request: UnifiedRequest) -> UnifiedResponse:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        choice = response.choices[0]
        return UnifiedResponse(
            provider=self.provider_name,
            model=self.deployment_name,
            content=choice.message.content or "",
            usage={"total_tokens": response.usage.total_tokens if response.usage else 0},
        )
