from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("my-account/", views.my_account, name="my_account"),
    path("soil-reports/", views.soil_reports, name="soil_reports"),
    path("soil-reports/<int:pk>/", views.soil_report_detail, name="soil_report_detail"),
    path("student-records/", views.student_records, name="student_records"),
    path("soil-samples/", views.soil_samples, name="soil_samples"),
    path("student-feedback/", views.student_feedback, name="student_feedback"),
]
