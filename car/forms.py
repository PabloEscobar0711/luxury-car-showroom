"""Forms used across the showroom experience."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Booking, Brand, Car, ContactInquiry


class StyledFormMixin:
    """Adds consistent Bootstrap-friendly classes to forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs["class"] = "form-select"
            elif isinstance(widget, forms.Textarea):
                widget.attrs["class"] = "form-control"
                widget.attrs.setdefault("rows", 4)
            else:
                widget.attrs["class"] = "form-control"

            widget.attrs.setdefault("autocomplete", "off")
            if field.help_text:
                widget.attrs.setdefault("aria-label", field.label or field_name.replace("_", " ").title())


class ShowroomAuthenticationForm(StyledFormMixin, AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))


class SignUpForm(StyledFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={"placeholder": "First name"}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={"placeholder": "Last name"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email address"}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name", "").strip()
        user.last_name = self.cleaned_data.get("last_name", "").strip()
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CarFilterForm(StyledFormMixin, forms.Form):
    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "Search model or brand"}),
    )
    brand = forms.ModelChoiceField(queryset=Brand.objects.none(), required=False, empty_label="All brands")
    fuel_type = forms.ChoiceField(
        required=False,
        choices=[("", "All fuel types"), *Car.FUEL_CHOICES],
    )
    min_price = forms.DecimalField(required=False, min_value=0, decimal_places=0, max_digits=12)
    max_price = forms.DecimalField(required=False, min_value=0, decimal_places=0, max_digits=12)

    def __init__(self, *args, **kwargs):
        brand_queryset = kwargs.pop("brand_queryset", Brand.objects.order_by("name"))
        super().__init__(*args, **kwargs)
        self.fields["brand"].queryset = brand_queryset
        self.fields["min_price"].widget.attrs["placeholder"] = "Min price"
        self.fields["max_price"].widget.attrs["placeholder"] = "Max price"

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get("min_price")
        max_price = cleaned_data.get("max_price")
        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError("Minimum price cannot be greater than maximum price.")
        return cleaned_data


class TestDriveBookingForm(StyledFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preferred_date"].widget.attrs["min"] = timezone.localdate().isoformat()

    class Meta:
        model = Booking
        fields = ("preferred_date", "notes")
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"placeholder": "Tell us your preferred time or any requirements"}),
        }

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data["preferred_date"]
        if preferred_date < timezone.localdate():
            raise forms.ValidationError("Please choose a date from today onward.")
        return preferred_date


class ContactDealerForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ("name", "email", "phone", "car", "subject", "message")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your full name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email address"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
            "subject": forms.TextInput(attrs={"placeholder": "Subject"}),
            "message": forms.Textarea(attrs={"placeholder": "Tell us what you need"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["car"].required = False
        self.fields["car"].queryset = Car.objects.select_related("brand").order_by("brand__name", "name")

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        digits = "".join(character for character in phone if character.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError("Enter a valid phone number with at least 10 digits.")
        return phone
