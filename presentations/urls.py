from django.urls import path

from . import views

app_name = "presentations"

urlpatterns = [
    path("", views.library, name="library"),
    path("upload/", views.UploadView.as_view(), name="upload"),
    path("<int:pk>/", views.detail, name="detail"),
    path("<int:pk>/retry/", views.retry, name="retry"),
    path("<int:pk>/delete/", views.delete, name="delete"),
    path("status-feed/", views.status_feed, name="status_feed"),
]
