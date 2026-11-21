from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Dish


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class DishForm(forms.ModelForm):
    new_photo = forms.ImageField(required=False, label="Photo (JPG or PNG, under 4 MB)")
    remove_photo = forms.BooleanField(required=False, label="Remove the current photo")

    class Meta:
        model = Dish
        fields = ["category", "name", "description", "price", "emoji", "is_available"]

    def save(self, commit=True):
        dish = super().save(commit=False)
        upload = self.cleaned_data.get("new_photo")
        if upload:
            dish.set_photo(upload)
        elif self.cleaned_data.get("remove_photo"):
            dish.clear_photo()
        if commit:
            dish.save()
        return dish


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
