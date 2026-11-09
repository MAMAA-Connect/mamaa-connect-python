import json
import boto3
from mamaa_connect.core import BaseAIAdapter, Provider, UnifiedRequest, UnifiedResponse


class AWSBedrockAdapter(BaseAIAdapter):
    def __init__(
        self,
        region_name: str = "us-east-1",
        model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0",
    ):
        self.model_id = model_id
        self.client = boto3.client("bedrock-runtime", region_name=region_name)

    @property
    def provider_name(self) -> Provider:
        return Provider.AWS

    def generate(self, request: UnifiedRequest) -> UnifiedResponse:
        messages = [{"role": m.role, "content": m.content} for m in request.messages if m.role != "system"]
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": messages,
        }
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(payload),
        )
        result = json.loads(response["body"].read())
        return UnifiedResponse(
            provider=self.provider_name,
            model=self.model_id,
            content=result["content"][0]["text"],
            usage=result.get("usage", {}),
        )
