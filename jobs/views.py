from functools import wraps

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import JobForm
from .models import Application, Job

def recruiter_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_recruiter():
            messages.error(request, "That page is for recruiter accounts.")
            return redirect("jobs:seeker_dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


def seeker_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_seeker():
            messages.error(request, "That page is for job seeker accounts.")
            return redirect("jobs:recruiter_dashboard")
        return view_func(request, *args, **kwargs)
    return wrapper


def home(request):
    jobs = Job.objects.filter(status=Job.Status.LIVE)[:6]
    stats = {
        "open_roles": Job.objects.filter(status=Job.Status.LIVE).count(),
        "companies": Job.objects.filter(status=Job.Status.LIVE).values("company").distinct().count(),
        "hires": Application.objects.filter(stage=Application.Stage.HIRED).count(),
    }
    return render(request, "home.html", {"jobs": jobs, "stats": stats})


def job_list(request):
    jobs = Job.objects.filter(status=Job.Status.LIVE)
    return render(request, "job_list.html", {"jobs": jobs})


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, status=Job.Status.LIVE)
    already_applied = False
    if request.user.is_authenticated and request.user.is_seeker():
        already_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    return render(request, "job_detail.html", {"job": job, "already_applied": already_applied})


@seeker_required
def apply_to_job(request, pk):
    job = get_object_or_404(Job, pk=pk, status=Job.Status.LIVE)
    Application.objects.get_or_create(job=job, applicant=request.user)
    messages.success(request, f"Applied to {job.title} at {job.company}.")
    return redirect("jobs:seeker_dashboard")


@recruiter_required
def post_job(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, f'"{job.title}" was posted.')
            return redirect("jobs:recruiter_dashboard")
    else:
        form = JobForm(initial={"company": request.user.organization})
    return render(request, "post_job.html", {"form": form})


@recruiter_required
def recruiter_dashboard(request):
    jobs = Job.objects.filter(recruiter=request.user)
    applications = Application.objects.filter(job__recruiter=request.user).select_related("job", "applicant")

    pipeline = {stage: [] for stage, _ in Application.Stage.choices if stage != Application.Stage.REJECTED}
    for app in applications:
        if app.stage in pipeline:
            pipeline[app.stage].append(app)

    stats = {
        "open_roles": jobs.filter(status=Job.Status.LIVE).count(),
        "new_applicants": applications.filter(stage=Application.Stage.APPLIED).count(),
        "interviews": applications.filter(stage=Application.Stage.INTERVIEW).count(),
        "offers": applications.filter(stage=Application.Stage.OFFER).count(),
    }

    context = {
        "jobs": jobs,
        "pipeline": pipeline,
        "stage_choices": [c for c in Application.Stage.choices if c[0] != Application.Stage.REJECTED],
        "stats": stats,
    }
    return render(request, "recruiter_dashboard.html", context)


@recruiter_required
def advance_stage(request, application_id):
    application = get_object_or_404(Application, pk=application_id, job__recruiter=request.user)
    next_stage = application.next_stage()
    if next_stage:
        application.stage = next_stage
        application.save()
        messages.success(request, f"Moved {application.applicant} to {application.get_stage_display()}.")
    return redirect("jobs:recruiter_dashboard")


@recruiter_required
def reject_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id, job__recruiter=request.user)
    application.stage = Application.Stage.REJECTED
    application.save()
    messages.info(request, f"{application.applicant} marked as not moving forward.")
    return redirect("jobs:recruiter_dashboard")


@seeker_required
def seeker_dashboard(request):
    applications = Application.objects.filter(applicant=request.user).select_related("job")
    applied_job_ids = applications.values_list("job_id", flat=True)
    recommended = Job.objects.filter(status=Job.Status.LIVE).exclude(id__in=applied_job_ids)[:3]

    context = {
        "applications": applications,
        "recommended": recommended,
    }
    return render(request, "seeker_dashboard.html", context)
