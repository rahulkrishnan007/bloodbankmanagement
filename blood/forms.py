from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from . import models
from donor.models import BLOOD_GROUP_CHOICES


class StyledFormMixin:
    """Gives every widget the Bootstrap look used across the site."""

    def _style(self):
        for field in self.fields.values():
            w = field.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs['class'] = 'custom-control-input'
            elif isinstance(w, forms.FileInput):
                w.attrs['class'] = 'form-control-file file-x'
            elif isinstance(w, forms.Select):
                w.attrs['class'] = 'custom-select'
            else:
                w.attrs['class'] = 'form-control'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


def clean_mobile_number(value):
    digits = ''.join(ch for ch in value if ch.isdigit())
    if not 10 <= len(digits) <= 15:
        raise forms.ValidationError('Enter a valid mobile number (10 to 15 digits).')
    return value.strip()


class BaseUserForm(StyledFormMixin, forms.ModelForm):
    """Account part of the donor / patient signup."""
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['username'].help_text = ''

    def clean_password(self):
        pwd = self.cleaned_data['password']
        validate_password(pwd)
        return pwd


class BaseUserUpdateForm(StyledFormMixin, forms.ModelForm):
    """Used when editing an existing account: the password is optional."""
    new_password = forms.CharField(
        widget=forms.PasswordInput(render_value=False), required=False,
        label='New password', help_text='Leave empty to keep the current password.')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''

    def clean_new_password(self):
        pwd = self.cleaned_data.get('new_password')
        if pwd:
            validate_password(pwd, self.instance)
        return pwd


class BloodForm(StyledFormMixin, forms.ModelForm):
    bloodgroup = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES, label='Blood group')
    unit = forms.IntegerField(min_value=0, max_value=100000, label='Stock (in ml)')

    class Meta:
        model = models.Stock
        fields = ['bloodgroup', 'unit']


class RequestForm(StyledFormMixin, forms.ModelForm):
    bloodgroup = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES, label='Blood group')
    unit = forms.IntegerField(min_value=50, max_value=3000, label='Unit (in ml)')
    required_by = forms.DateField(
        required=False, label='Required by',
        widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = models.BloodRequest
        fields = ['patient_name', 'patient_age', 'reason', 'bloodgroup', 'unit',
                  'priority', 'hospital', 'required_by']
        widgets = {'reason': forms.Textarea(attrs={'rows': 3})}
        labels = {'patient_name': 'Patient name', 'patient_age': 'Patient age',
                  'hospital': 'Hospital / location'}

    def clean_patient_age(self):
        age = self.cleaned_data['patient_age']
        if age > 120:
            raise forms.ValidationError('Enter a valid age.')
        return age

    def clean_required_by(self):
        d = self.cleaned_data.get('required_by')
        if d and d < timezone.localdate():
            raise forms.ValidationError('The date cannot be in the past.')
        return d


class CampForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = models.Camp
        fields = ['title', 'venue', 'city', 'date', 'start_time', 'end_time',
                  'organizer', 'contact', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        data = super().clean()
        s, e = data.get('start_time'), data.get('end_time')
        if s and e and e <= s:
            raise forms.ValidationError('End time must be after the start time.')
        return data
