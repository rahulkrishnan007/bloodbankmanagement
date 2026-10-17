import csv
from datetime import date

from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse

from donor.models import BLOOD_GROUPS
from .models import Notification, Stock


def ensure_stock():
    """Make sure one Stock row exists for each of the 8 blood groups."""
    for g in BLOOD_GROUPS:
        Stock.objects.get_or_create(bloodgroup=g, defaults={'unit': 0})


def stock_level(unit):
    if unit < settings.CRITICAL_STOCK_ML:
        return 'critical'
    if unit < settings.LOW_STOCK_ML:
        return 'low'
    return 'good'


def stock_overview():
    """List of dicts (one per blood group, in a fixed order) with a level and bar %."""
    ensure_stock()
    by_group = {s.bloodgroup: s for s in Stock.objects.all()}
    out = []
    for g in BLOOD_GROUPS:
        s = by_group[g]
        out.append({
            'id': s.id,
            'group': g,
            'unit': s.unit,
            'level': stock_level(s.unit),
            'percent': min(100, round(s.unit * 100 / settings.FULL_STOCK_ML)),
        })
    return out


def notify(user, message, level='info', link=''):
    if user is not None:
        Notification.objects.create(user=user, message=message, level=level, link=link)


def paginate(request, queryset, per_page=10):
    return Paginator(queryset, per_page).get_page(request.GET.get('page'))


def csv_response(filename, header, rows):
    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = f'attachment; filename="{filename}-{date.today()}.csv"'
    w = csv.writer(resp)
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return resp
