from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

class SignupForm(forms.Form):
    role = forms.ChoiceField(
        choices=User.Role.choices,
        widget=forms.RadioSelect,
    )
    full_name = forms.CharField(max_length=150, label="Full name")
    email = forms.EmailField(label="Email")
    organization = forms.CharField(
        max_length=150, required=False, label="Company name"
    )
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords don't match.")
        if p1 and len(p1) < 8:
            self.add_error("password1", "Use at least 8 characters.")
        return cleaned

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["email"],
            email=data["email"],
            password=data["password1"],
            role=data["role"],
            organization=data.get("organization", ""),
        )
        full_name = data["full_name"].strip()
        if " " in full_name:
            first, last = full_name.split(" ", 1)
        else:
            first, last = full_name, ""
        user.first_name = first
        user.last_name = last
        user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
