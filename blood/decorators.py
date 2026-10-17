from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def _role_required(check, login_url, label):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{login_url}?next={request.path}")
            if not check(request.user):
                messages.error(request, f"That page is only available to {label}.")
                return redirect('afterlogin')
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def is_donor(user):
    return user.groups.filter(name='DONOR').exists()


def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


def is_admin(user):
    return user.is_staff or user.is_superuser


admin_required = _role_required(is_admin, '/adminlogin', 'administrators')
donor_required = _role_required(is_donor, '/donor/donorlogin', 'donors')
patient_required = _role_required(is_patient, '/patient/patientlogin', 'patients')
