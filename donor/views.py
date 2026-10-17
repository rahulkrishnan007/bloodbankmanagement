from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from blood import forms as bforms
from blood import models as bmodels
from blood.decorators import donor_required
from blood.utils import notify, paginate
from . import forms, models


def donor_signup_view(request):
    userForm = forms.DonorUserForm()
    donorForm = forms.DonorForm()
    if request.method == 'POST':
        userForm = forms.DonorUserForm(request.POST)
        donorForm = forms.DonorForm(request.POST, request.FILES)
        if userForm.is_valid() and donorForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()
            donor = donorForm.save(commit=False)
            donor.user = user
            donor.save()
            Group.objects.get_or_create(name='DONOR')[0].user_set.add(user)
            messages.success(request, 'Account created! Please log in.')
            return redirect('donorlogin')
    return render(request, 'donor/donorsignup.html', {'userForm': userForm, 'donorForm': donorForm})


@donor_required
def donor_dashboard_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    mine = bmodels.BloodRequest.objects.filter(request_by_donor=donor)
    ctx = {
        'donor': donor,
        'requestpending': mine.filter(status='Pending').count(),
        'requestapproved': mine.filter(status='Approved').count(),
        'requestmade': mine.count(),
        'requestrejected': mine.filter(status='Rejected').count(),
        'recent_donations': donor.blooddonate_set.all()[:4],
        'camps': bmodels.Camp.objects.filter(date__gte=timezone.localdate())[:3],
        'gap': settings.DONATION_GAP_DAYS,
        'progress': max(0, min(100, round((settings.DONATION_GAP_DAYS - donor.days_to_eligible) * 100 / settings.DONATION_GAP_DAYS))),
    }
    return render(request, 'donor/donor_dashboard.html', ctx)


@donor_required
def donate_blood_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    if not donor.is_eligible:
        messages.warning(request, f"You can donate again on {donor.next_eligible_date:%d %b %Y} "
                                  f"({donor.days_to_eligible} days to go).")
        return redirect('donor-dashboard')
    if donor.blooddonate_set.filter(status='Pending').exists():
        messages.info(request, 'You already have a donation waiting for approval.')
        return redirect('donation-history')
    form = forms.DonationForm(donor=donor)
    if request.method == 'POST':
        form = forms.DonationForm(request.POST, donor=donor)
        if form.is_valid():
            d = form.save(commit=False)
            d.donor = donor
            d.save()
            messages.success(request, 'Donation request sent. The blood bank will review it shortly.')
            return redirect('donation-history')
    return render(request, 'donor/donate_blood.html', {'donation_form': form, 'donor': donor})


@donor_required
def donation_history_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    page = paginate(request, donor.blooddonate_set.all())
    return render(request, 'donor/donation_history.html', {'page': page, 'donor': donor})


@donor_required
def make_request_view(request):
    form = bforms.RequestForm()
    if request.method == 'POST':
        form = bforms.RequestForm(request.POST)
        if form.is_valid():
            br = form.save(commit=False)
            br.request_by_donor = models.Donor.objects.get(user_id=request.user.id)
            br.save()
            messages.success(request, 'Blood request submitted.')
            return redirect('request-history')
    return render(request, 'donor/makerequest.html', {'request_form': form})


@donor_required
def request_history_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    qs = bmodels.BloodRequest.objects.filter(request_by_donor=donor)
    return render(request, 'donor/request_history.html', {'page': paginate(request, qs)})


@donor_required
def donor_profile_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    form = forms.DonorProfileForm(instance=donor)
    if request.method == 'POST':
        form = forms.DonorProfileForm(request.POST, request.FILES, instance=donor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('donor-profile')
    return render(request, 'donor/profile.html', {'form': form, 'donor': donor})


@donor_required
@require_POST
def toggle_availability_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    donor.is_available = not donor.is_available
    donor.save(update_fields=['is_available'])
    messages.success(request, 'You are now visible to people searching for donors.'
                     if donor.is_available else 'You are now hidden from the donor search.')
    return redirect('donor-dashboard')


@donor_required
def certificate_view(request, pk):
    donor = models.Donor.objects.get(user_id=request.user.id)
    donation = get_object_or_404(models.BloodDonate, pk=pk, donor=donor, status='Approved')
    return render(request, 'donor/certificate.html', {'donation': donation, 'donor': donor})
