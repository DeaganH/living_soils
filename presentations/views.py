from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View

from .forms import PresentationUploadForm
from .models import Feedback, Presentation
from .tasks import enqueue_presentation

try:
    from PyPDF2 import PdfReader
except Exception:  # pragma: no cover - defensive import for minimal environments
    PdfReader = None


@login_required
def library(request):
    presentations = (
        Presentation.objects.filter(uploaded_by=request.user)
        .select_related("feedback")
        .order_by("-uploaded_at")
    )
    return render(request, "presentations/library.html", {"presentations": presentations})


class UploadView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "presentations/upload.html", {"form": PresentationUploadForm()})

    def post(self, request):
        form = PresentationUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, "presentations/upload.html", {"form": form}, status=400)

        presentation = form.save(commit=False)
        presentation.uploaded_by = request.user
        presentation.file_name = presentation.file.name
        presentation.file_size = presentation.file.size
        presentation.page_count = _extract_page_count(presentation)
        presentation.save()
        enqueue_presentation(presentation.id)
        messages.success(request, "Upload received. Processing will continue in the background.")
        return redirect(reverse("dashboard:soil_reports"))


def _extract_page_count(presentation: Presentation):
    if not PdfReader:
        return None
    try:
        presentation.file.seek(0)
        reader = PdfReader(presentation.file)
        return len(reader.pages)
    except Exception:
        return None


@login_required
def detail(request, pk: int):
    presentation = get_object_or_404(
        Presentation.objects.filter(uploaded_by=request.user).select_related("feedback"),
        pk=pk,
    )
    context = {
        "presentation": presentation,
        "feedback": getattr(presentation, "feedback", None),
    }
    return render(request, "presentations/detail.html", context)


@login_required
def status_feed(request):
    """Simple JSON feed to poll for processing completion."""
    since = request.GET.get("since")
    qs = Presentation.objects.filter(uploaded_by=request.user, status=Presentation.Status.COMPLETE)
    if since:
        try:
            dt = timezone.datetime.fromisoformat(since)
            qs = qs.filter(uploaded_at__gt=dt)
        except ValueError:
            pass
    payload = [
        {
            "id": p.id,
            "status": p.status,
            "file_name": p.file_name,
        }
        for p in qs.order_by("-uploaded_at")[:50]
    ]
    return JsonResponse({"items": payload})


@permission_required("presentations.delete_presentation")
def delete(request, pk: int):
    presentation = get_object_or_404(Presentation.objects.filter(uploaded_by=request.user), pk=pk)
    if request.method == "POST":
        presentation.file.delete(save=False)
        presentation.delete()
        messages.success(request, "Presentation deleted.")
        return redirect(reverse("dashboard:soil_reports"))
    return render(request, "presentations/confirm_delete.html", {"presentation": presentation})
