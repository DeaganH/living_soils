from django.contrib import admin
from django.urls import include, path

from .views import home, logged_out, modal_login, modal_logout, modal_signup

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/modal-login/", modal_login, name="modal_login"),
    path("accounts/modal-signup/", modal_signup, name="modal_signup"),
    path("accounts/logout/", modal_logout, name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("logged-out/", logged_out, name="logged_out"),
    path("dashboard/", include("dashboard.urls")),
    path("presentations/", include("presentations.urls")),
    path("", home, name="home"),
]
