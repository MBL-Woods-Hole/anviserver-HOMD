#from registration.forms import RegistrationForm
from registration.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django import forms

import re

class UserRegForm(UserCreationForm):
    username = forms.CharField(max_length=30, required=True, label='Username', help_text="Required. 30 characters or fewer. Letters, digits and _ only.")

    fullname = forms.CharField(max_length=100, required=False, label='Full name')
    institution = forms.CharField(max_length=100, required=False)
    orcid = forms.CharField(max_length=100, required=False, label='ORCID')

    def clean_username(self):
        username = self.cleaned_data['username'].lower()

        if not re.match(r'^[a-z0-9_]*$', username):
            raise ValidationError("") # help text already contains required information

        return username


class SettingsForm(forms.Form):
    fullname = forms.CharField(max_length=100, required=False, label='Full name')
    institution = forms.CharField(max_length=100, required=False)
    orcid = forms.CharField(max_length=100, required=False, label='ORCID')
