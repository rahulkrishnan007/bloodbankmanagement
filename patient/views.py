from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render

from blood import forms as bforms
from blood import models as bmodels
from blood.decorators import patient_required
from blood.utils import paginate
from . import forms, models


def patient_signup_view(request):
    userForm = forms.PatientUserForm()
    patientForm = forms.PatientForm()
    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            patient = patientForm.save(commit=False)
            patient.user = user
            patient.save()
            Group.objects.get_or_create(name='PATIENT')[0].user_set.add(user)
            messages.success(request, 'Account created! Please log in.')
            return redirect('patientlogin')
    return render(request, 'patient/patientsignup.html',
                  {'userForm': userForm, 'patientForm': patientForm})


@patient_required
def patient_dashboard_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    mine = bmodels.BloodRequest.objects.filter(request_by_patient=patient)
    ctx = {
        'patient': patient,
        'requestpending': mine.filter(status='Pending').count(),
        'requestapproved': mine.filter(status='Approved').count(),
        'requestmade': mine.count(),
        'requestrejected': mine.filter(status='Rejected').count(),
        'recent': mine[:4],
    }
    return render(request, 'patient/patient_dashboard.html', ctx)


@patient_required
def make_request_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    initial = {'patient_name': patient.get_name, 'patient_age': patient.age,
               'bloodgroup': patient.bloodgroup, 'reason': patient.disease}
    form = bforms.RequestForm(initial=initial)
    if request.method == 'POST':
        form = bforms.RequestForm(request.POST)
        if form.is_valid():
            br = form.save(commit=False)
            br.request_by_patient = patient
            br.save()
            messages.success(request, 'Blood request submitted.')
            return redirect('my-request')
    return render(request, 'patient/makerequest.html', {'request_form': form})


@patient_required
def my_request_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    qs = bmodels.BloodRequest.objects.filter(request_by_patient=patient)
    return render(request, 'patient/my_request.html', {'page': paginate(request, qs)})


@patient_required
def patient_profile_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    form = forms.PatientForm(instance=patient)
    if request.method == 'POST':
        form = forms.PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('patient-profile')
    return render(request, 'patient/profile.html', {'form': form, 'patient': patient})
