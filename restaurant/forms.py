from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Dish


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ["category", "name", "description", "price", "photo", "emoji", "is_available"]


class CustomerAuthForm(AuthenticationForm):
    """Customer sign-in. Staff accounts must use the admin page instead."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.is_staff:
            raise forms.ValidationError(
                "This is a restaurant staff account. Please sign in on the admin page.", code="staff"
            )


class AdminAuthForm(AuthenticationForm):
    """Admin sign-in. Only staff accounts are allowed in."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                "This page is for restaurant staff only. Customers sign in on the main site.", code="not_staff"
            )
