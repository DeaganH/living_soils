from django.contrib import admin

from .models import Feedback, Presentation


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = (
        "file_name",
        "uploaded_by",
        "uploaded_at",
        "status",
        "file_size",
        "page_count",
    )
    list_filter = ("status", "uploaded_at")
    search_fields = ("file_name", "uploaded_by__username")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "presentation",
        "api_timestamp",
        "input_tokens",
        "output_tokens",
    )
    search_fields = ("presentation__file_name",)
