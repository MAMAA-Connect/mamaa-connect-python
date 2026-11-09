from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class Provider(str, Enum):
    GOOGLE = "alphabet_google"
    AWS = "amazon_aws"
    AZURE = "microsoft_azure"
    META = "meta_llama"
    APPLE = "apple_local"


class UnifiedMessage(BaseModel):
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Text payload")


class UnifiedRequest(BaseModel):
    messages: List[UnifiedMessage]
    temperature: float = 0.7
    max_tokens: int = 1024
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UnifiedResponse(BaseModel):
    provider: Provider
    model: str
    content: str
    usage: Dict[str, int] = Field(default_factory=dict)
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAIAdapter(ABC):
    """Universal contract that every Big Tech adapter must implement."""

    @property
    @abstractmethod
    def provider_name(self) -> Provider:
        pass

    @abstractmethod
    def generate(self, request: UnifiedRequest) -> UnifiedResponse:
        pass


class MamaaRouter:
    """Core routing engine with automatic cross-cloud fallback."""

    def __init__(self, adapters: List[BaseAIAdapter]):
        if not adapters:
            raise ValueError("At least one Big Tech adapter must be registered.")
        self.adapters = {adapter.provider_name: adapter for adapter in adapters}
        self.priority_order = [adapter.provider_name for adapter in adapters]

    def execute(
        self,
        request: UnifiedRequest,
        preferred_provider: Optional[Provider] = None,
        enable_fallback: bool = True,
    ) -> UnifiedResponse:
        execution_queue = list(self.priority_order)

        if preferred_provider and preferred_provider in execution_queue:
            execution_queue.remove(preferred_provider)
            execution_queue.insert(0, preferred_provider)

        errors = {}
        for provider in execution_queue:
            adapter = self.adapters[provider]
            try:
                return adapter.generate(request)
            except Exception as exc:
                errors[provider.value] = str(exc)
                if not enable_fallback:
                    raise RuntimeError(f"Provider {provider.value} failed: {exc}") from exc

        raise RuntimeError(f"All Big Tech providers failed. Details: {errors}")
