from django import forms
from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class PhoneForm(forms.Form):
    phone_number = forms.CharField(max_length=20, validators=[phone_regex])

class CodeForm(forms.Form):
    code = forms.CharField(max_length=4)