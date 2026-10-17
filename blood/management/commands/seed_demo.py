import random
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from blood.models import BloodRequest, Camp, Stock
from blood.utils import ensure_stock
from donor.models import BloodDonate, Donor
from patient.models import Patient


class Command(BaseCommand):
    help = 'Create demo data (admin / donors / patients / camps) so the site can be explored right away.'

    def handle(self, *args, **opts):
        random.seed(7)
        ensure_stock()
        today = timezone.localdate()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin12345', first_name='Admin')
        dg = Group.objects.get_or_create(name='DONOR')[0]
        pg = Group.objects.get_or_create(name='PATIENT')[0]

        donors = []
        for i, (fn, ln, bg, city) in enumerate([
                ('Arun', 'Menon', 'O+', 'Kochi'), ('Meera', 'Nair', 'A+', 'Kochi'), ('Vishnu', 'Raj', 'B+', 'Thrissur'),
                ('Anjali', 'Das', 'O-', 'Kozhikode'), ('Rahul', 'Krishnan', 'AB+', 'Ernakulam'), ('Sneha', 'Paul', 'A-', 'Kochi')]):
            u, new = User.objects.get_or_create(username=f'donor{i+1}', defaults={'first_name': fn, 'last_name': ln})
            if new:
                u.set_password('demo12345'); u.save(); dg.user_set.add(u)
                Donor.objects.create(user=u, bloodgroup=bg, address=city, mobile=f'98470000{i:02d}',
                                     gender='Male' if i % 2 == 0 else 'Female', weight=60 + i)
            donors.append(Donor.objects.get(user=u))

        patients = []
        for i, (fn, ln, bg, dis) in enumerate([('Suresh', 'Kumar', 'O+', 'Anaemia'), ('Lakshmi', 'Devi', 'B+', 'Surgery'), ('Jose', 'Thomas', 'A+', 'Thalassemia')]):
            u, new = User.objects.get_or_create(username=f'patient{i+1}', defaults={'first_name': fn, 'last_name': ln})
            if new:
                u.set_password('demo12345'); u.save(); pg.user_set.add(u)
                Patient.objects.create(user=u, age=35 + i * 7, bloodgroup=bg, disease=dis, doctorname='Dr. Ramesh',
                                       address='Kochi', mobile=f'97450000{i:02d}')
            patients.append(Patient.objects.get(user=u))

        if not BloodDonate.objects.exists():
            for n, d in enumerate(donors):
                for k in range(1 + n % 3):
                    x = BloodDonate.objects.create(donor=d, age=25 + n, bloodgroup=d.bloodgroup, unit=350 + 50 * (k % 2),
                                                   status='Approved' if not (n == 5 and k == 0) else 'Pending')
                    BloodDonate.objects.filter(pk=x.pk).update(date=today - timedelta(days=random.randint(100, 170) - k * 30 if n < 5 else 3))
            totals = {}
            for x in BloodDonate.objects.filter(status='Approved'):
                totals[x.bloodgroup] = totals.get(x.bloodgroup, 0) + x.unit
            base = {'A+': 1800, 'A-': 650, 'B+': 2400, 'B-': 300, 'AB+': 1200, 'AB-': 220, 'O+': 3100, 'O-': 540}
            for g, u in base.items():
                Stock.objects.filter(bloodgroup=g).update(unit=u)

        if not BloodRequest.objects.exists():
            rows = [(patients[0], 'Suresh Kumar', 41, 'Severe anaemia', 'O+', 450, 'Emergency', 'Amrita Hospital', 'Pending', 0),
                    (patients[1], 'Lakshmi Devi', 48, 'Heart surgery', 'B+', 900, 'Urgent', 'Lisie Hospital', 'Pending', 2),
                    (patients[2], 'Jose Thomas', 55, 'Thalassemia transfusion', 'A+', 350, 'Normal', 'Medical Trust', 'Approved', 12),
                    (patients[0], 'Suresh Kumar', 41, 'Routine transfusion', 'O+', 350, 'Normal', 'Rajagiri Hospital', 'Rejected', 25),
                    (patients[1], 'Baby of Lakshmi', 1, 'Newborn jaundice', 'B+', 150, 'Urgent', 'Lisie Hospital', 'Approved', 40)]
            for p, nm, age, why, bg, u, pr, h, st, ago in rows:
                r = BloodRequest.objects.create(request_by_patient=p, patient_name=nm, patient_age=age, reason=why, bloodgroup=bg,
                                                unit=u, priority=pr, hospital=h, status=st)
                BloodRequest.objects.filter(pk=r.pk).update(date=today - timedelta(days=ago))

        if not Camp.objects.exists():
            for t, v, c, days, s, e in [('World Blood Donor Day Camp', 'Town Hall', 'Kochi', 6, '09:00', '15:00'),
                                        ('Campus Donation Drive', 'CUSAT Auditorium', 'Kochi', 18, '10:00', '16:00'),
                                        ('Community Health Camp', 'Parish Hall', 'Thrissur', 33, '09:30', '13:30')]:
                Camp.objects.create(title=t, venue=v, city=c, date=today + timedelta(days=days), start_time=s, end_time=e,
                                    organizer='LifeFlow Blood Bank', contact='0484 2200000',
                                    description='Free health check-up, refreshments and a donor certificate for every donor.')
        self.stdout.write(self.style.SUCCESS(
            'Demo data ready.  Admin: admin / admin12345   Donor: donor1 / demo12345   Patient: patient1 / demo12345'))
