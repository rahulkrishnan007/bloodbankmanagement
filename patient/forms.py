from django import forms

from blood.forms import (BaseUserForm, BaseUserUpdateForm, StyledFormMixin,
                         clean_mobile_number)
from donor.models import BLOOD_GROUP_CHOICES
from . import models


class PatientUserForm(BaseUserForm):
    pass


class PatientUserUpdateForm(BaseUserUpdateForm):
    pass


class PatientForm(StyledFormMixin, forms.ModelForm):
    bloodgroup = forms.ChoiceField(choices=[('', 'Choose...')] + BLOOD_GROUP_CHOICES, label='Blood group')

    class Meta:
        model = models.Patient
        fields = ['age', 'bloodgroup', 'disease', 'address', 'doctorname', 'mobile', 'profile_pic']
        labels = {'doctorname': 'Doctor name', 'profile_pic': 'Profile photo'}

    def clean_mobile(self):
        return clean_mobile_number(self.cleaned_data['mobile'])

    def clean_age(self):
        age = self.cleaned_data['age']
        if age > 120:
            raise forms.ValidationError('Enter a valid age.')
        return age
