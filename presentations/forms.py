from django import forms

from .models import Presentation


class PresentationUploadForm(forms.ModelForm):
    class Meta:
        model = Presentation
        fields = ["file"]

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        if uploaded.content_type != "application/pdf" and not uploaded.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Only PDF uploads are allowed.")
        if uploaded.size > 200 * 1024 * 1024:
            raise forms.ValidationError("File exceeds 200MB limit.")
        return uploaded
