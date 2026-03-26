import logging
import json
import time
from typing import Optional

from django.db import transaction
from django.utils import timezone
from django_q.tasks import async_task

from .models import Feedback, Presentation
from .services import LLMClientError, call_llm_api

logger = logging.getLogger(__name__)

MAX_PROCESSING_ATTEMPTS = 5
INITIAL_BACKOFF_SECONDS = 2


def enqueue_presentation(presentation_id: int) -> None:
    async_task("presentations.tasks.process_presentation", presentation_id)


def process_presentation(presentation_id: int) -> None:
    try:
        presentation = Presentation.objects.select_for_update().get(pk=presentation_id)
    except Presentation.DoesNotExist:
        logger.warning("Presentation %s no longer exists", presentation_id)
        return

    presentation.status = Presentation.Status.PROCESSING
    presentation.error_message = ""
    presentation.save(update_fields=["status", "error_message"])

    attempts = 0
    error: Optional[str] = None

    while attempts < MAX_PROCESSING_ATTEMPTS:
        attempts += 1
        try:
            with presentation.file.open("rb") as fh:
                api_response = call_llm_api(fh, presentation.file_name)
            _persist_feedback(presentation, api_response)
            presentation.status = Presentation.Status.COMPLETE
            presentation.error_message = ""
            presentation.save(update_fields=["status", "error_message"])
            return
        except (LLMClientError, Exception) as exc:  # broad to capture network/json issues
            error = str(exc)
            logger.exception("Processing failed for %s attempt %s", presentation_id, attempts)
            if attempts < MAX_PROCESSING_ATTEMPTS:
                backoff_seconds = INITIAL_BACKOFF_SECONDS * (2 ** (attempts - 1))
                time.sleep(backoff_seconds)

    presentation.status = Presentation.Status.FAILED
    presentation.error_message = error or "Processing failed"
    presentation.save(update_fields=["status", "error_message"])


def _persist_feedback(presentation: Presentation, api_response) -> None:
    report_data = json.dumps(api_response, indent=2, sort_keys=True, default=_json_default)

    with transaction.atomic():
        Feedback.objects.update_or_create(
            presentation=presentation,
            defaults={
                "summary": "Report Data",
                "detailed_feedback": report_data,
                "input_tokens": api_response.get("input_tokens") or 0,
                "output_tokens": api_response.get("output_tokens") or 0,
                "api_timestamp": api_response.get("datetimestamp") or timezone.now(),
            },
        )


def _json_default(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
