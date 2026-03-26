from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from presentations.models import Presentation

from .forms import SoilSampleForm, StudentFeedbackForm
from .models import SoilSample, StudentFeedbackSubmission, StudentReport


@login_required
def index(request):
    return redirect(reverse("dashboard:soil_reports"))


@login_required
def my_account(request):
    return render(request, "dashboard/account.html")


@login_required
def soil_reports(request):
    presentations = (
        Presentation.objects.filter(uploaded_by=request.user)
        .select_related("feedback")
        .order_by("-uploaded_at")
    )
    return render(request, "dashboard/soil_reports.html", {"presentations": presentations})


@login_required
def soil_report_detail(request, pk: int):
    presentation = get_object_or_404(
        Presentation.objects.filter(uploaded_by=request.user).select_related("feedback"),
        pk=pk,
    )
    return render(
        request,
        "dashboard/soil_report_detail.html",
        {"presentation": presentation, "feedback": getattr(presentation, "feedback", None)},
    )


@login_required
@require_http_methods(["GET"])
def student_records(request):
    reports = StudentReport.objects.filter(student=request.user).order_by("-report_date", "-created_at")
    return render(request, "dashboard/student_records.html", {"reports": reports})


@login_required
@require_http_methods(["GET", "POST"])
def soil_samples(request):
    if request.method == "POST":
        form = SoilSampleForm(request.POST)
        if form.is_valid():
            sample: SoilSample = form.save(commit=False)
            sample.owner = request.user
            sample.save()
            messages.success(request, "Soil sample saved.")
            return redirect(reverse("dashboard:soil_samples"))
    else:
        form = SoilSampleForm()

    samples = SoilSample.objects.filter(owner=request.user).order_by("-created_at")
    return render(request, "dashboard/soil_samples.html", {"form": form, "samples": samples})


@login_required
@require_http_methods(["GET", "POST"])
def student_feedback(request):
    if request.method == "POST":
        form = StudentFeedbackForm(request.POST)
        if form.is_valid():
            submission: StudentFeedbackSubmission = form.save(commit=False)
            submission.owner = request.user
            submission.save()

            to_email = getattr(settings, "STUDENT_FEEDBACK_TO_EMAIL", "")
            if to_email:
                try:
                    send_mail(
                        subject=f"[Living Soils] {submission.subject}",
                        message=f"From: {request.user.email or request.user.username}\n\n{submission.message}",
                        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                        recipient_list=[to_email],
                        fail_silently=False,
                    )
                    messages.success(request, "Feedback sent. Thank you!")
                except Exception:
                    messages.warning(
                        request,
                        "Feedback saved, but email sending is not configured."
                    )
            else:
                messages.success(request, "Feedback saved. Thank you!")

            return redirect(reverse("dashboard:student_feedback"))
    else:
        form = StudentFeedbackForm()

    return render(request, "dashboard/student_feedback.html", {"form": form})
