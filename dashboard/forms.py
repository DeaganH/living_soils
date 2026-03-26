from django import forms

from .models import SoilSample, StudentFeedbackSubmission


class SoilSampleForm(forms.ModelForm):
    class Meta:
        model = SoilSample
        fields = ["plot_number", "sample_depth_cm", "latitude", "longitude", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class StudentFeedbackForm(forms.ModelForm):
    class Meta:
        model = StudentFeedbackSubmission
        fields = ["subject", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 6}),
        }
