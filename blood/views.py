from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Case, Count, IntegerField, Q, Sum, Value, When
from django.db.models.functions import TruncMonth
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from donor import forms as dforms
from donor import models as dmodels
from donor.models import BLOOD_GROUPS
from patient import forms as pforms
from patient import models as pmodels

from . import forms, models
from .decorators import admin_required, is_admin, is_donor, is_patient
from .utils import csv_response, notify, paginate, stock_level, stock_overview

# Who can give blood to whom (donor group -> recipient groups)
COMPATIBILITY = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'],
}

PRIORITY_ORDER = Case(
    When(priority='Emergency', then=Value(0)),
    When(priority='Urgent', then=Value(1)),
    default=Value(2), output_field=IntegerField())


# ==========================================================================
# Public pages
# ==========================================================================
def home_view(request):
    if request.user.is_authenticated:
        return redirect('afterlogin')
    approved = dmodels.BloodDonate.objects.filter(status='Approved')
    ctx = {
        'stock': stock_overview(),
        'stat_donors': dmodels.Donor.objects.count(),
        'stat_donations': approved.count(),
        'stat_lives': approved.count() * 3,
        'stat_fulfilled': models.BloodRequest.objects.filter(status='Approved').count(),
        'camps': models.Camp.objects.filter(date__gte=timezone.localdate())[:3],
    }
    return render(request, 'blood/index.html', ctx)


def compatibility_view(request):
    rows = [{'donor': d, 'recipients': COMPATIBILITY[d]} for d in BLOOD_GROUPS]
    receive = {r: [d for d in BLOOD_GROUPS if r in COMPATIBILITY[d]] for r in BLOOD_GROUPS}
    return render(request, 'blood/compatibility.html',
                  {'rows': rows, 'groups': BLOOD_GROUPS, 'receive': receive})


def camps_view(request):
    today = timezone.localdate()
    ctx = {
        'upcoming': models.Camp.objects.filter(date__gte=today),
        'past': models.Camp.objects.filter(date__lt=today).order_by('-date')[:6],
    }
    return render(request, 'blood/camps.html', ctx)


@login_required(login_url='/adminlogin')
def afterlogin_view(request):
    user = request.user
    if is_donor(user):
        return redirect('/donor/donor-dashboard')
    if is_patient(user):
        return redirect('/patient/patient-dashboard')
    if is_admin(user):
        return redirect('admin-dashboard')
    messages.info(request, 'Your account has no role yet. Please sign up as a donor or patient.')
    return redirect('/')


@login_required(login_url='/adminlogin')
def find_donors_view(request):
    """Search available donors by blood group / city (any logged-in user)."""
    bg = request.GET.get('bloodgroup', '')
    q = request.GET.get('q', '').strip()
    donors = dmodels.Donor.objects.select_related('user').filter(is_available=True)
    own = dmodels.Donor.objects.filter(user=request.user).first()
    if own:
        donors = donors.exclude(pk=own.pk)
    if bg:
        donors = donors.filter(bloodgroup=bg)
    if q:
        donors = donors.filter(Q(address__icontains=q) | Q(user__first_name__icontains=q)
                               | Q(user__last_name__icontains=q))
    donors = [d for d in donors if d.is_eligible]
    layout = _layout_for(request.user)
    return render(request, 'blood/find_donors.html',
                  {'donors': donors, 'bg': bg, 'q': q, 'groups': BLOOD_GROUPS, 'layout': layout})


def _layout_for(user):
    if is_admin(user):
        return 'blood/adminbase.html'
    if is_donor(user):
        return 'donor/donorbase.html'
    return 'patient/patientbase.html'


# ==========================================================================
# Notifications & request cancel (donor, patient, admin)
# ==========================================================================
@login_required(login_url='/adminlogin')
def notifications_view(request):
    items = models.Notification.objects.filter(user=request.user)
    page = paginate(request, items, 15)
    return render(request, 'blood/notifications.html',
                  {'page': page, 'layout': _layout_for(request.user)})


@login_required(login_url='/adminlogin')
@require_POST
def notifications_read_view(request):
    models.Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')


@login_required(login_url='/adminlogin')
@require_POST
def cancel_request_view(request, pk):
    req = get_object_or_404(models.BloodRequest, pk=pk, status='Pending')
    owner = req.requester_user
    if owner != request.user:
        raise Http404
    req.delete()
    messages.success(request, 'Your blood request was cancelled.')
    return redirect('afterlogin')


# ==========================================================================
# Admin dashboard
# ==========================================================================
def _last_months(n=6):
    today = timezone.localdate().replace(day=1)
    months = []
    y, m = today.year, today.month
    for _ in range(n):
        months.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return list(reversed(months))


@admin_required
def admin_dashboard_view(request):
    stock = stock_overview()
    req = models.BloodRequest.objects
    don = dmodels.BloodDonate.objects

    months = _last_months(6)
    start = timezone.localdate().replace(year=months[0][0], month=months[0][1], day=1)
    don_by_month = {(r['m'].year, r['m'].month): r['t'] for r in
                    don.filter(status='Approved', date__gte=start)
                    .annotate(m=TruncMonth('date')).values('m').annotate(t=Sum('unit'))}
    req_by_month = {(r['m'].year, r['m'].month): r['t'] for r in
                    req.filter(date__gte=start)
                    .annotate(m=TruncMonth('date')).values('m').annotate(t=Count('id'))}
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    chart_data = {
        'groups': [s['group'] for s in stock],
        'stock': [s['unit'] for s in stock],
        'status': [req.filter(status=s).count() for s in ('Pending', 'Approved', 'Rejected')],
        'months': [f"{month_names[m - 1]} {str(y)[2:]}" for y, m in months],
        'donated': [don_by_month.get(k, 0) for k in months],
        'requested': [req_by_month.get(k, 0) for k in months],
    }

    ctx = {
        'stock': stock,
        'low_stock': [s for s in stock if s['level'] != 'good'],
        'totaldonors': dmodels.Donor.objects.count(),
        'totalpatients': pmodels.Patient.objects.count(),
        'totalbloodunit': models.Stock.objects.aggregate(t=Sum('unit'))['t'] or 0,
        'totalrequest': req.count(),
        'totalapprovedrequest': req.filter(status='Approved').count(),
        'pending_requests': req.filter(status='Pending').count(),
        'pending_donations': don.filter(status='Pending').count(),
        'emergency_requests': req.filter(status='Pending', priority='Emergency').count(),
        'recent_requests': req.order_by('-id')[:5],
        'recent_donations': don.order_by('-id')[:5],
        'upcoming_camps': models.Camp.objects.filter(date__gte=timezone.localdate())[:3],
        'chart_data': chart_data,
    }
    return render(request, 'blood/admin_dashboard.html', ctx)


@admin_required
def admin_blood_view(request):
    form = forms.BloodForm()
    if request.method == 'POST':
        form = forms.BloodForm(request.POST)
        if form.is_valid():
            stock = models.Stock.objects.get(bloodgroup=form.cleaned_data['bloodgroup'])
            stock.unit = form.cleaned_data['unit']
            stock.save()
            messages.success(request, f"{stock.bloodgroup} stock updated to {stock.unit} ml.")
            return redirect('admin-blood')
    return render(request, 'blood/admin_blood.html', {'bloodForm': form, 'stock': stock_overview()})


# ==========================================================================
# Donors / patients management
# ==========================================================================
@admin_required
def admin_donor_view(request):
    q = request.GET.get('q', '').strip()
    bg = request.GET.get('bloodgroup', '')
    donors = dmodels.Donor.objects.select_related('user').order_by('-id')
    if q:
        donors = donors.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q)
                               | Q(address__icontains=q) | Q(mobile__icontains=q)
                               | Q(user__username__icontains=q))
    if bg:
        donors = donors.filter(bloodgroup=bg)
    return render(request, 'blood/admin_donor.html',
                  {'page': paginate(request, donors), 'q': q, 'bg': bg, 'groups': BLOOD_GROUPS})


@admin_required
def update_donor_view(request, pk):
    donor = get_object_or_404(dmodels.Donor, pk=pk)
    user = donor.user
    userForm = dforms.DonorUserUpdateForm(instance=user)
    donorForm = dforms.DonorForm(instance=donor)
    if request.method == 'POST':
        userForm = dforms.DonorUserUpdateForm(request.POST, instance=user)
        donorForm = dforms.DonorForm(request.POST, request.FILES, instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user = userForm.save()
            if userForm.cleaned_data.get('new_password'):
                user.set_password(userForm.cleaned_data['new_password'])
                user.save()
            donorForm.save()
            messages.success(request, 'Donor details updated.')
            return redirect('admin-donor')
    return render(request, 'blood/update_donor.html', {'userForm': userForm, 'donorForm': donorForm, 'donor': donor})


@admin_required
@require_POST
def delete_donor_view(request, pk):
    donor = get_object_or_404(dmodels.Donor, pk=pk)
    donor.user.delete()
    messages.success(request, 'Donor deleted.')
    return redirect('admin-donor')


@admin_required
def admin_patient_view(request):
    q = request.GET.get('q', '').strip()
    bg = request.GET.get('bloodgroup', '')
    patients = pmodels.Patient.objects.select_related('user').order_by('-id')
    if q:
        patients = patients.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q)
                                   | Q(disease__icontains=q) | Q(doctorname__icontains=q)
                                   | Q(mobile__icontains=q))
    if bg:
        patients = patients.filter(bloodgroup=bg)
    return render(request, 'blood/admin_patient.html',
                  {'page': paginate(request, patients), 'q': q, 'bg': bg, 'groups': BLOOD_GROUPS})


@admin_required
def update_patient_view(request, pk):
    patient = get_object_or_404(pmodels.Patient, pk=pk)
    user = patient.user
    userForm = pforms.PatientUserUpdateForm(instance=user)
    patientForm = pforms.PatientForm(instance=patient)
    if request.method == 'POST':
        userForm = pforms.PatientUserUpdateForm(request.POST, instance=user)
        patientForm = pforms.PatientForm(request.POST, request.FILES, instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save()
            if userForm.cleaned_data.get('new_password'):
                user.set_password(userForm.cleaned_data['new_password'])
                user.save()
            patientForm.save()
            messages.success(request, 'Patient details updated.')
            return redirect('admin-patient')
    return render(request, 'blood/update_patient.html',
                  {'userForm': userForm, 'patientForm': patientForm, 'patient': patient})


@admin_required
@require_POST
def delete_patient_view(request, pk):
    patient = get_object_or_404(pmodels.Patient, pk=pk)
    patient.user.delete()
    messages.success(request, 'Patient deleted.')
    return redirect('admin-patient')


# ==========================================================================
# Blood requests
# ==========================================================================
@admin_required
def admin_request_view(request):
    requests_ = (models.BloodRequest.objects.filter(status='Pending')
                 .annotate(p=PRIORITY_ORDER).order_by('p', 'id'))
    # tell the admin at a glance whether the stock can cover each request
    stock = {s['group']: s['unit'] for s in stock_overview()}
    for r in requests_:
        r.stock_ok = stock.get(r.bloodgroup, 0) >= r.unit
        r.stock_available = stock.get(r.bloodgroup, 0)
    return render(request, 'blood/admin_request.html', {'requests': requests_})


@admin_required
def admin_request_history_view(request):
    status = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()
    reqs = models.BloodRequest.objects.exclude(status='Pending')
    if status in ('Approved', 'Rejected'):
        reqs = reqs.filter(status=status)
    if q:
        reqs = reqs.filter(Q(patient_name__icontains=q) | Q(hospital__icontains=q)
                           | Q(reason__icontains=q))
    return render(request, 'blood/admin_request_history.html',
                  {'page': paginate(request, reqs), 'status': status, 'q': q})


@admin_required
@require_POST
@transaction.atomic
def update_approve_status_view(request, pk):
    req = get_object_or_404(models.BloodRequest, pk=pk)
    if req.status != 'Pending':
        messages.warning(request, 'This request was already processed.')
        return redirect('admin-request')
    stock = models.Stock.objects.select_for_update().get(bloodgroup=req.bloodgroup)
    if stock.unit >= req.unit:
        stock.unit -= req.unit
        stock.save()
        req.status = 'Approved'
        req.save()
        notify(req.requester_user,
               f"Your request for {req.unit} ml of {req.bloodgroup} blood was approved.",
               'success', '/patient/my-request' if req.request_by_patient else '/donor/request-history')
        messages.success(request, f"Request approved. {req.unit} ml of {req.bloodgroup} deducted from stock.")
    else:
        messages.error(request, f"Not enough {req.bloodgroup} blood in stock - only {stock.unit} ml available.")
    return redirect('admin-request')


@admin_required
@require_POST
def update_reject_status_view(request, pk):
    req = get_object_or_404(models.BloodRequest, pk=pk)
    if req.status == 'Pending':
        req.status = 'Rejected'
        req.save()
        notify(req.requester_user,
               f"Your request for {req.unit} ml of {req.bloodgroup} blood was rejected.",
               'danger', '/patient/my-request' if req.request_by_patient else '/donor/request-history')
        messages.info(request, 'Request rejected.')
    return redirect('admin-request')


# ==========================================================================
# Donations
# ==========================================================================
@admin_required
def admin_donation_view(request):
    status = request.GET.get('status', '')
    donations = dmodels.BloodDonate.objects.select_related('donor__user')
    if status in ('Pending', 'Approved', 'Rejected'):
        donations = donations.filter(status=status)
    return render(request, 'blood/admin_donation.html',
                  {'page': paginate(request, donations), 'status': status})


@admin_required
@require_POST
@transaction.atomic
def approve_donation_view(request, pk):
    donation = get_object_or_404(dmodels.BloodDonate, pk=pk)
    if donation.status != 'Pending':
        messages.warning(request, 'This donation was already processed.')
        return redirect('admin-donation')
    stock = models.Stock.objects.select_for_update().get(bloodgroup=donation.bloodgroup)
    stock.unit += donation.unit
    stock.save()
    donation.status = 'Approved'
    donation.save()
    notify(donation.donor.user,
           f"Thank you! Your donation of {donation.unit} ml was approved and added to the stock.",
           'success', '/donor/donation-history')
    messages.success(request, f"Donation approved. {donation.unit} ml added to {donation.bloodgroup} stock.")
    return redirect('admin-donation')


@admin_required
@require_POST
def reject_donation_view(request, pk):
    donation = get_object_or_404(dmodels.BloodDonate, pk=pk)
    if donation.status == 'Pending':
        donation.status = 'Rejected'
        donation.save()
        notify(donation.donor.user, "Your donation request was not approved this time.",
               'danger', '/donor/donation-history')
        messages.info(request, 'Donation rejected.')
    return redirect('admin-donation')


# ==========================================================================
# Camps
# ==========================================================================
@admin_required
def admin_camps_view(request):
    form = forms.CampForm()
    if request.method == 'POST':
        form = forms.CampForm(request.POST)
        if form.is_valid():
            camp = form.save()
            messages.success(request, f'Camp "{camp.title}" published.')
            return redirect('admin-camps')
    return render(request, 'blood/admin_camps.html',
                  {'form': form, 'camps': models.Camp.objects.order_by('-date')})


@admin_required
@require_POST
def delete_camp_view(request, pk):
    get_object_or_404(models.Camp, pk=pk).delete()
    messages.success(request, 'Camp removed.')
    return redirect('admin-camps')


# ==========================================================================
# CSV exports
# ==========================================================================
@admin_required
def export_donors_view(request):
    rows = [(d.get_name, d.user.username, d.bloodgroup, d.gender, d.weight or '', d.address,
             d.mobile, d.total_donations, d.total_units, d.last_donation_date or '')
            for d in dmodels.Donor.objects.select_related('user')]
    return csv_response('donors', ['Name', 'Username', 'Blood group', 'Gender', 'Weight', 'Address',
                                   'Mobile', 'Donations', 'Total ml', 'Last donation'], rows)


@admin_required
def export_requests_view(request):
    rows = [(r.id, r.patient_name, r.patient_age, r.bloodgroup, r.unit, r.priority, r.hospital,
             r.required_by or '', r.reason, r.status, r.date)
            for r in models.BloodRequest.objects.all()]
    return csv_response('blood-requests', ['ID', 'Patient', 'Age', 'Blood group', 'ml', 'Priority',
                                           'Hospital', 'Required by', 'Reason', 'Status', 'Date'], rows)


@admin_required
def export_donations_view(request):
    rows = [(d.id, d.donor.get_name, d.bloodgroup, d.unit, d.age, d.disease, d.status, d.date)
            for d in dmodels.BloodDonate.objects.select_related('donor__user')]
    return csv_response('donations', ['ID', 'Donor', 'Blood group', 'ml', 'Age', 'Disease', 'Status', 'Date'], rows)
