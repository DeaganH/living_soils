from django.conf import settings
from django.db import models


class StudentRecord(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_records")
    lecturer_feedback = models.TextField(blank=True)
    assessment_report = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Student record for {self.owner}"  # pragma: no cover


class StudentReport(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_reports",
    )
    report_date = models.DateField()
    title = models.CharField(max_length=140, blank=True)
    pdf = models.FileField(upload_to="student_reports/%Y/%m/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Report for {self.student} on {self.report_date}"  # pragma: no cover


class SoilSample(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="soil_samples")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    plot_number = models.CharField(max_length=80, blank=True)
    sample_depth_cm = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Soil sample {self.id} for {self.owner}"  # pragma: no cover


class StudentFeedbackSubmission(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedback_submissions")
    subject = models.CharField(max_length=140)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Feedback from {self.owner}: {self.subject}"  # pragma: no cover
