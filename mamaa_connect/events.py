import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from cloudevents.http import CloudEvent, to_structured
from mamaa_connect.core import Provider


def create_cross_cloud_event(
    source_provider: Provider,
    target_provider: Provider,
    event_type: str,
    payload: Dict[str, Any],
) -> tuple[Dict[str, str], bytes]:
    """Wraps any Big Tech payload into a CNCF-compliant CloudEvent."""
    attributes = {
        "id": str(uuid.uuid4()),
        "type": f"org.mamaa-connect.{event_type}",
        "source": f"urn:mamaa:{source_provider.value}",
        "target": f"urn:mamaa:{target_provider.value}",
        "time": datetime.now(timezone.utc).isoformat(),
    }
    event = CloudEvent(attributes, payload)
    headers, body = to_structured(event)
    return headers, body
