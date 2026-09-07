from django import forms

from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title", "company", "location", "job_type",
            "salary_min", "salary_max", "description", "status",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }
