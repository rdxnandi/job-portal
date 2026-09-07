from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Berth profile", {"fields": ("role", "organization")}),
    )
    list_display = ("username", "email", "role", "organization", "is_staff")
