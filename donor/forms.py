from django import forms
from django.conf import settings

from blood.forms import (BaseUserForm, BaseUserUpdateForm, StyledFormMixin,
                         clean_mobile_number)
from . import models
from .models import BLOOD_GROUP_CHOICES


class DonorUserForm(BaseUserForm):
    pass


class DonorUserUpdateForm(BaseUserUpdateForm):
    pass


class DonorForm(StyledFormMixin, forms.ModelForm):
    bloodgroup = forms.ChoiceField(choices=[('', 'Choose...')] + BLOOD_GROUP_CHOICES, label='Blood group')
    gender = forms.ChoiceField(choices=[('', 'Choose...')] + models.Donor.GENDERS, required=False)

    class Meta:
        model = models.Donor
        fields = ['bloodgroup', 'gender', 'weight', 'address', 'mobile', 'profile_pic']
        labels = {'weight': 'Weight (kg)', 'profile_pic': 'Profile photo'}

    def clean_mobile(self):
        return clean_mobile_number(self.cleaned_data['mobile'])

    def clean_weight(self):
        w = self.cleaned_data.get('weight')
        if w is not None and not 30 <= w <= 250:
            raise forms.ValidationError('Enter a valid weight in kg.')
        return w


class DonorProfileForm(DonorForm):
    class Meta(DonorForm.Meta):
        fields = ['bloodgroup', 'gender', 'weight', 'address', 'mobile', 'profile_pic', 'is_available']
        labels = {**DonorForm.Meta.labels, 'is_available': 'Show me in the "Find Donors" list'}


class DonationForm(StyledFormMixin, forms.ModelForm):
    bloodgroup = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES, label='Blood group')
    unit = forms.IntegerField(min_value=100, max_value=500, label='Unit (in ml)',
                              help_text='A standard donation is 350 - 450 ml.')

    class Meta:
        model = models.BloodDonate
        fields = ['age', 'bloodgroup', 'disease', 'unit']
        labels = {'disease': 'Any disease / medication?'}

    def __init__(self, *args, donor=None, **kwargs):
        self.donor = donor
        super().__init__(*args, **kwargs)
        if donor and not self.is_bound:
            self.fields['bloodgroup'].initial = donor.bloodgroup

    def clean_age(self):
        age = self.cleaned_data['age']
        if not settings.DONOR_MIN_AGE <= age <= settings.DONOR_MAX_AGE:
            raise forms.ValidationError(
                f'Donors must be between {settings.DONOR_MIN_AGE} and {settings.DONOR_MAX_AGE} years old.')
        return age

    def clean_bloodgroup(self):
        bg = self.cleaned_data['bloodgroup']
        if self.donor and bg != self.donor.bloodgroup:
            raise forms.ValidationError(f'Your registered blood group is {self.donor.bloodgroup}.')
        return bg
