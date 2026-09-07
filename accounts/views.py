from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .forms import SignupForm

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard_redirect")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard_redirect")
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})


@login_required
def dashboard_redirect(request):
    """Sends a freshly logged-in user to the dashboard that matches their role."""
    if request.user.is_recruiter():
        return redirect("jobs:recruiter_dashboard")
    return redirect("jobs:seeker_dashboard")
