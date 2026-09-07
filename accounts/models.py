from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom user with a role that decides which dashboard they land on."""

    class Role(models.TextChoices):
        RECRUITER = "recruiter", "Recruiter"
        SEEKER = "seeker", "Seeker"

    role = models.CharField(max_length=10, choices=Role.choices)

    # For a recruiter this holds their company name.
    # For a seeker this holds their current/most recent job title.
    organization = models.CharField(max_length=150, blank=True)

    def is_recruiter(self):
        return self.role == self.Role.RECRUITER

    def is_seeker(self):
        return self.role == self.Role.SEEKER

    def initials(self):
        name = self.get_full_name() or self.username
        parts = name.split()
        letters = "".join(p[0] for p in parts[:2])
        return letters.upper() or "?"

    def __str__(self):
        return self.get_full_name() or self.username
