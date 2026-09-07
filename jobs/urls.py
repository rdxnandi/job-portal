from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/apply/", views.apply_to_job, name="apply_to_job"),
    path("post-job/", views.post_job, name="post_job"),
    path("dashboard/recruiter/", views.recruiter_dashboard, name="recruiter_dashboard"),
    path("dashboard/seeker/", views.seeker_dashboard, name="seeker_dashboard"),
    path("applications/<int:application_id>/advance/", views.advance_stage, name="advance_stage"),
    path("applications/<int:application_id>/reject/", views.reject_application, name="reject_application"),
]
