from .models import Notification


def site_context(request):
    """Adds role flags and the unread-notification count to every template."""
    ctx = {'SITE_NAME': 'LifeFlow Blood Bank'}
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated:
        ctx['unread_count'] = Notification.objects.filter(user=user, is_read=False).count()
        ctx['is_admin_user'] = user.is_staff
        ctx['is_donor_user'] = user.groups.filter(name='DONOR').exists()
        ctx['is_patient_user'] = user.groups.filter(name='PATIENT').exists()
    return ctx
