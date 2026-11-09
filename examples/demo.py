from mamaa_connect import (
    MamaaRouter,
    Provider,
    UnifiedMessage,
    UnifiedRequest,
    create_cross_cloud_event,
)
from mamaa_connect.adapters import (
    GoogleGeminiAdapter,
    AWSBedrockAdapter,
    AzureOpenAIAdapter,
    MetaLlamaAdapter,
)


def main():
    # 1. Initialize unified router with multiple Big Tech providers
    router = MamaaRouter(
        adapters=[
            GoogleGeminiAdapter(),
            AWSBedrockAdapter(),
            AzureOpenAIAdapter(),
            MetaLlamaAdapter(),
        ]
    )

    # 2. Build a single provider-agnostic request
    request = UnifiedRequest(
        messages=[
            UnifiedMessage(role="system", content="You are an enterprise cloud architect."),
            UnifiedMessage(role="user", content="Explain how to connect AWS S3 and Google BigQuery."),
        ],
        temperature=0.3,
    )

    # 3. Execute with automatic fallback (tries Google first, falls back to AWS/Azure/Meta if needed)
    response = router.execute(request, preferred_provider=Provider.GOOGLE, enable_fallback=True)
    print(f"[{response.provider.value} | {response.model}]:\n{response.content}\n")

    # 4. Emit a standardized CloudEvent from Meta to AWS
    headers, body = create_cross_cloud_event(
        source_provider=Provider.META,
        target_provider=Provider.AWS,
        event_type="ai.inference.completed",
        payload={"model": response.model, "summary": response.content[:100]},
    )
    print("CloudEvent Headers:", headers)
    print("CloudEvent Body:", body.decode("utf-8"))


if __name__ == "__main__":
    main()
