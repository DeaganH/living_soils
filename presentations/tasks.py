import logging
from typing import Optional

from django.db import transaction
from django.utils import timezone
from django_q.tasks import async_task

from .models import Feedback, Presentation
from .services import LLMClientError, call_llm_api

logger = logging.getLogger(__name__)


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
    max_attempts = 3  # initial attempt + 2 retries
    error: Optional[str] = None

    while attempts < max_attempts:
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

    presentation.status = Presentation.Status.FAILED
    presentation.error_message = error or "Processing failed"
    presentation.save(update_fields=["status", "error_message"])


def _persist_feedback(presentation: Presentation, api_response) -> None:
    with transaction.atomic():
        Feedback.objects.update_or_create(
            presentation=presentation,
            defaults={
                "summary": api_response.get("summary", ""),
                "detailed_feedback": api_response.get("detailed_feedback", ""),
                "input_tokens": api_response.get("input_tokens") or 0,
                "output_tokens": api_response.get("output_tokens") or 0,
                "api_timestamp": api_response.get("time_stamp") or timezone.now(),
            },
        )
