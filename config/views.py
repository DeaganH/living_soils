from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout as auth_logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import SignUpForm


def home(request):
    if request.user.is_authenticated:
        return redirect(reverse("dashboard:soil_reports"))
    return render(request, "home.html")


def logged_out(request):
    return render(request, "logged_out.html")


def _safe_next_url(request, default: str) -> str:
    next_url = request.POST.get("next") or request.GET.get("next") or ""
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    return default


def _with_query(url: str, **params) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    for key, value in params.items():
        query[key] = str(value)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _normalize_next_after_auth(next_url: str) -> str:
    """Prevent redirect loops back to the logged-out confirmation page."""
    try:
        path = urlsplit(next_url).path
    except Exception:
        return next_url

    if path == reverse("logged_out"):
        return reverse("dashboard:soil_reports")
    return next_url


@require_POST
def modal_login(request):
    if request.user.is_authenticated:
        return redirect(_safe_next_url(request, reverse("dashboard:soil_reports")))

    identifier_raw = (request.POST.get("email") or "").strip()
    password = request.POST.get("password") or ""
    next_url = _normalize_next_after_auth(_safe_next_url(request, reverse("dashboard:soil_reports")))

    if not identifier_raw or not password:
        messages.error(request, "Please enter your email and password.")
        return redirect(_with_query(next_url, auth="login", auth_error=1))

    User = get_user_model()
    username = identifier_raw
    if "@" in identifier_raw:
        identifier_email = identifier_raw.lower()
        user_by_email = User.objects.filter(email__iexact=identifier_email).only("username").first()
        if user_by_email:
            username = user_by_email.username

    from django.contrib.auth import authenticate

    user = authenticate(request, username=username, password=password)
    if user is None:
        messages.error(request, "Invalid email or password.")
        return redirect(_with_query(next_url, auth="login", auth_error=1))

    login(request, user)
    return redirect(next_url)


@require_POST
def modal_signup(request):
    if request.user.is_authenticated:
        return redirect(_safe_next_url(request, reverse("dashboard:soil_reports")))

    next_url = _normalize_next_after_auth(_safe_next_url(request, reverse("dashboard:soil_reports")))
    form = SignUpForm(request.POST)
    if not form.is_valid():
        for err in form.errors.get("__all__", []) or []:
            messages.error(request, err)
        for field in ("email", "password1", "password2"):
            for err in form.errors.get(field, []) or []:
                messages.error(request, err)
        return redirect(_with_query(next_url, auth="signup", auth_error=1))

    email = form.cleaned_data["email"]
    password = form.cleaned_data["password1"]

    try:
        validate_password(password)
    except ValidationError as exc:
        for msg in exc.messages:
            messages.error(request, msg)
        return redirect(_with_query(next_url, auth="signup", auth_error=1))

    User = get_user_model()
    user = User.objects.create_user(username=email, email=email, password=password)
    login(request, user)
    return redirect(next_url)


@require_POST
def modal_logout(request):
    auth_logout(request)
    return redirect(reverse("logged_out"))
