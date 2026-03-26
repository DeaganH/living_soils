from django.conf import settings
from django.db import models


class Presentation(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETE = "COMPLETE", "Complete"
        FAILED = "FAILED", "Failed"

    file = models.FileField(upload_to="presentations/")
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveBigIntegerField()
    page_count = models.PositiveIntegerField(null=True, blank=True)

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.file_name


class Feedback(models.Model):
    presentation = models.OneToOneField(Presentation, on_delete=models.CASCADE, related_name="feedback")
    summary = models.TextField()
    detailed_feedback = models.TextField()
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    api_timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Feedback for {self.presentation.file_name}"
