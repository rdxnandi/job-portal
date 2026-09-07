from django.contrib import admin

from .models import Application, Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "recruiter", "status", "created_at")
    list_filter = ("status", "job_type")

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant", "job", "stage", "applied_at")
    list_filter = ("stage",)
