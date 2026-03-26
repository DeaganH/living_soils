from datetime import datetime
from typing import Any, Dict

import requests
from django.conf import settings


class LLMClientError(Exception):
    pass


def call_llm_api(file_obj, file_name: str) -> Dict[str, Any]:
    if not settings.LLM_API_URL:
        raise LLMClientError("LLM_API_URL is not configured")

    headers = {"Authorization": f"Bearer {settings.LLM_API_KEY}"} if settings.LLM_API_KEY else {}
    response = requests.post(
        settings.LLM_API_URL,
        files={"file": (file_name, file_obj, "application/pdf")},
        headers=headers,
        timeout=60,
    )
    if response.status_code >= 400:
        raise LLMClientError(f"LLM API error: {response.status_code} {response.text}")

    data = response.json()
    # Basic schema validation
    required_keys = {
        "summary",
        "detailed_feedback",
        "input_tokens",
        "output_tokens",
        "time_stamp",
    }
    if not required_keys.issubset(data.keys()):
        raise LLMClientError("LLM API response missing required fields")

    # Normalize timestamp
    if isinstance(data["time_stamp"], str):
        data["time_stamp"] = datetime.fromisoformat(data["time_stamp"].replace("Z", "+00:00"))

    return data
