from django.contrib import admin

from .models import SoilSample, StudentFeedbackSubmission, StudentReport

@admin.register(StudentReport)
class StudentReportAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "report_date", "title", "created_at")
    list_filter = ("report_date",)
    search_fields = ("student__username", "student__email", "title")


@admin.register(SoilSample)
class SoilSampleAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "plot_number", "latitude", "longitude", "created_at")
    search_fields = ("owner__username", "owner__email", "plot_number")


@admin.register(StudentFeedbackSubmission)
class StudentFeedbackSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "subject", "created_at")
    search_fields = ("owner__username", "owner__email", "subject")
