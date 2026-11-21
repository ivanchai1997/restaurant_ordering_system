import base64
import binascii
from io import BytesIO

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Dish


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class DishForm(forms.ModelForm):
    new_photo = forms.ImageField(required=False, label="Photo (JPG or PNG)")
    cropped_photo = forms.CharField(required=False, widget=forms.HiddenInput)  # filled in by the crop tool
    remove_photo = forms.BooleanField(required=False, label="Remove the current photo")

    class Meta:
        model = Dish
        fields = ["category", "name", "description", "price", "emoji", "is_available"]

    def clean_cropped_photo(self):
        data = self.cleaned_data.get("cropped_photo") or ""
        if not data:
            return b""
        if not data.startswith("data:image/") or "," not in data:
            raise forms.ValidationError("That photo could not be read.")
        try:
            raw = base64.b64decode(data.split(",", 1)[1], validate=True)
        except (binascii.Error, ValueError):
            raise forms.ValidationError("That photo could not be read.")
        if len(raw) > 3_000_000:
            raise forms.ValidationError("That photo is too large. Try a smaller one.")
        try:
            from PIL import Image

            Image.open(BytesIO(raw)).verify()
        except Exception:
            raise forms.ValidationError("That photo could not be read.")
        return raw

    def save(self, commit=True):
        dish = super().save(commit=False)
        cropped = self.cleaned_data.get("cropped_photo")
        upload = self.cleaned_data.get("new_photo")
        if cropped:
            dish.set_photo(BytesIO(cropped))
        elif upload:
            dish.set_photo(upload)  # no browser crop: centre-crop to the box on the server
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
