from datetime import datetime
from typing import Any, Dict

import requests
from django.conf import settings


class LLMClientError(Exception):
    pass


def call_llm_api(file_obj, file_name: str) -> Dict[str, Any]:
    if not settings.LLM_API_URL:
        raise LLMClientError("LLM_API_URL is not configured")

    file_obj.seek(0)
    if not file_obj.read(1):
        raise LLMClientError("Uploaded PDF is empty")
    file_obj.seek(0)

    headers = {"x-authorization": settings.LLM_API_KEY} if settings.LLM_API_KEY else {}
    response = requests.post(
        settings.LLM_API_URL,
        files={"file": (file_name, file_obj, "application/pdf")},
        headers=headers,
        timeout=90,
    )
    if response.status_code >= 400:
        raise LLMClientError(f"LLM API error: {response.status_code} {response.text}")

    data = response.json()
    # Basic schema validation
    required_keys = {'datetimestamp',
                      'file_name', 
                      'ocr_used', 
                      'Analysis', 
                      'Client', 
                      'Report_Number', 
                      'Number_of_Samples', 
                      'Sample_Type', 
                      'Condition', 
                      'Delivery_Date', 
                      'Delivery_Time', 
                      'Order_Number', 
                      'test_results'
                      }
    
    if not required_keys.issubset(data.keys()):
        raise LLMClientError("LLM API response missing required fields")

    # Normalize timestamp
    if isinstance(data["datetimestamp"], str):
        data["datetimestamp"] = datetime.fromisoformat(data["datetimestamp"].replace("Z", "+00:00"))

    return data
