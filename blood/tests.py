from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blood.models import BloodRequest, Camp, Notification, Stock
from donor.models import BloodDonate, Donor
from patient.models import Patient

PW = 'Str0ng-Passw0rd!'


def make_admin():
    return User.objects.create_superuser('boss', 'b@x.com', PW, first_name='Boss')


def make_donor(username='dono', group='O+'):
    u = User.objects.create_user(username, password=PW, first_name='Dona', last_name='Tor')
    Group.objects.get_or_create(name='DONOR')[0].user_set.add(u)
    return Donor.objects.create(user=u, bloodgroup=group, address='Kochi', mobile='9876543210')


def make_patient(username='pat', group='O+'):
    u = User.objects.create_user(username, password=PW, first_name='Pat', last_name='Ient')
    Group.objects.get_or_create(name='PATIENT')[0].user_set.add(u)
    return Patient.objects.create(user=u, age=40, bloodgroup=group, disease='Anaemia',
                                  doctorname='Dr. A', address='Kochi', mobile='9876543211')


class PublicPages(TestCase):
    def test_public_pages_render(self):
        for url in ['/', '/compatibility', '/camps', '/adminlogin', '/donor/donorlogin',
                    '/patient/patientlogin', '/donor/donorsignup', '/patient/patientsignup']:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_stock_seeded(self):
        self.assertEqual(Stock.objects.count(), 8)

    def test_pages_need_login(self):
        for url in ['/admin-dashboard', '/donor/donor-dashboard', '/patient/patient-dashboard',
                    '/find-donors', '/notifications']:
            self.assertEqual(self.client.get(url).status_code, 302, url)


class Signup(TestCase):
    def test_donor_signup_and_login(self):
        r = self.client.post('/donor/donorsignup', {
            'first_name': 'A', 'last_name': 'B', 'username': 'abd', 'password': PW,
            'bloodgroup': 'A+', 'gender': 'Male', 'weight': 70, 'address': 'Kochi', 'mobile': '9876543210'})
        self.assertRedirects(r, '/donor/donorlogin')
        self.assertTrue(Donor.objects.filter(user__username='abd').exists())
        self.assertTrue(self.client.login(username='abd', password=PW))
        self.assertRedirects(self.client.get('/afterlogin'), '/donor/donor-dashboard',
                             fetch_redirect_response=False)

    def test_invalid_signup_shows_errors(self):
        r = self.client.post('/donor/donorsignup', {'first_name': 'A', 'username': 'x', 'password': '123'})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(User.objects.filter(username='x').exists())

    def test_patient_signup(self):
        r = self.client.post('/patient/patientsignup', {
            'first_name': 'P', 'last_name': 'Q', 'username': 'pq', 'password': PW, 'age': 30,
            'bloodgroup': 'B+', 'disease': 'Fever', 'doctorname': 'Dr X', 'address': 'Kochi', 'mobile': '9999999999'})
        self.assertRedirects(r, '/patient/patientlogin')


class DonationFlow(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.donor = make_donor()

    def test_full_donation_cycle(self):
        self.client.login(username='dono', password=PW)
        self.assertEqual(self.client.get('/donor/donor-dashboard').status_code, 200)
        self.assertEqual(self.client.get('/donor/donate-blood').status_code, 200)
        # wrong blood group rejected
        r = self.client.post('/donor/donate-blood', {'age': 30, 'bloodgroup': 'A+', 'disease': 'None', 'unit': 350})
        self.assertEqual(BloodDonate.objects.count(), 0)
        # underage rejected
        self.client.post('/donor/donate-blood', {'age': 16, 'bloodgroup': 'O+', 'disease': 'None', 'unit': 350})
        self.assertEqual(BloodDonate.objects.count(), 0)
        r = self.client.post('/donor/donate-blood', {'age': 30, 'bloodgroup': 'O+', 'disease': 'None', 'unit': 350})
        self.assertRedirects(r, '/donor/donation-history')
        # second pending donation is blocked
        self.client.post('/donor/donate-blood', {'age': 30, 'bloodgroup': 'O+', 'disease': 'None', 'unit': 350})
        self.assertEqual(BloodDonate.objects.count(), 1)
        d = BloodDonate.objects.get()

        # donors cannot approve their own donation
        self.assertEqual(self.client.post(f'/approve-donation/{d.id}').status_code, 302)
        d.refresh_from_db(); self.assertEqual(d.status, 'Pending')

        self.client.logout(); self.client.login(username='boss', password=PW)
        self.assertEqual(self.client.get(f'/approve-donation/{d.id}').status_code, 405)  # GET not allowed
        self.client.post(f'/approve-donation/{d.id}')
        self.client.post(f'/approve-donation/{d.id}')  # double click must not double the stock
        self.assertEqual(Stock.objects.get(bloodgroup='O+').unit, 350)
        self.assertTrue(Notification.objects.filter(user=self.donor.user).exists())

        self.donor.refresh_from_db()
        self.assertFalse(self.donor.is_eligible)
        self.assertEqual(self.donor.total_units, 350)
        self.client.logout(); self.client.login(username='dono', password=PW)
        self.assertEqual(self.client.get(f'/donor/certificate/{d.id}').status_code, 200)
        self.assertRedirects(self.client.get('/donor/donate-blood'), '/donor/donor-dashboard',
                             fetch_redirect_response=False)
        self.assertEqual(self.client.get('/notifications').status_code, 200)

    def test_eligible_again_after_gap(self):
        d = BloodDonate.objects.create(donor=self.donor, age=30, bloodgroup='O+', unit=300, status='Approved')
        BloodDonate.objects.filter(pk=d.pk).update(date=timezone.localdate() - timedelta(days=91))
        self.assertTrue(Donor.objects.get(pk=self.donor.pk).is_eligible)

    def test_toggle_availability_and_find(self):
        self.client.login(username='dono', password=PW)
        self.client.post('/donor/toggle-availability')
        self.assertFalse(Donor.objects.get().is_available)
        self.client.post('/donor/toggle-availability')
        pat = make_patient()
        self.client.logout(); self.client.login(username='pat', password=PW)
        r = self.client.get('/find-donors?bloodgroup=O%2B')
        self.assertContains(r, 'Dona Tor')
        r = self.client.get('/find-donors?bloodgroup=A-')
        self.assertNotContains(r, 'Dona Tor')

    def test_profile_update(self):
        self.client.login(username='dono', password=PW)
        self.assertEqual(self.client.get('/donor/profile').status_code, 200)
        r = self.client.post('/donor/profile', {'bloodgroup': 'O+', 'gender': 'Female', 'weight': 60,
                                                 'address': 'Pune', 'mobile': '9876543210', 'is_available': 'on'})
        self.assertRedirects(r, '/donor/profile')
        self.assertEqual(Donor.objects.get().address, 'Pune')


class RequestFlow(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.patient = make_patient()
        self.client.login(username='pat', password=PW)

    def _request(self, unit=400, **extra):
        data = {'patient_name': 'Pat', 'patient_age': 40, 'reason': 'Surgery', 'bloodgroup': 'O+',
                'unit': unit, 'priority': 'Urgent', 'hospital': 'City Hospital'}
        data.update(extra)
        return self.client.post('/patient/make-request', data)

    def test_request_approve_and_stock_rules(self):
        self.assertEqual(self.client.get('/patient/make-request').status_code, 200)
        self.assertRedirects(self._request(400), '/patient/my-request')
        self.assertEqual(self.client.get('/patient/my-request').status_code, 200)
        req = BloodRequest.objects.get()
        self.assertEqual(req.priority, 'Urgent')

        self.client.logout(); self.client.login(username='boss', password=PW)
        self.assertEqual(self.client.get('/admin-request').status_code, 200)
        # no stock -> cannot approve
        self.client.post(f'/update-approve-status/{req.id}')
        req.refresh_from_db(); self.assertEqual(req.status, 'Pending')
        # exact stock -> approve (the original code wrongly refused this)
        Stock.objects.filter(bloodgroup='O+').update(unit=400)
        self.client.post(f'/update-approve-status/{req.id}')
        req.refresh_from_db(); self.assertEqual(req.status, 'Approved')
        self.assertEqual(Stock.objects.get(bloodgroup='O+').unit, 0)
        self.assertTrue(Notification.objects.filter(user=self.patient.user).exists())
        self.assertEqual(self.client.get('/admin-request-history?status=Approved').status_code, 200)

    def test_reject_and_cancel(self):
        self._request(300)
        req = BloodRequest.objects.get()
        self.client.post(f'/cancel-request/{req.id}')
        self.assertEqual(BloodRequest.objects.count(), 0)
        self._request(300)
        req = BloodRequest.objects.get()
        # another patient cannot cancel it
        make_patient('other')
        self.client.logout(); self.client.login(username='other', password=PW)
        self.assertEqual(self.client.post(f'/cancel-request/{req.id}').status_code, 404)
        self.client.logout(); self.client.login(username='boss', password=PW)
        self.client.post(f'/update-reject-status/{req.id}')
        req.refresh_from_db(); self.assertEqual(req.status, 'Rejected')

    def test_validation(self):
        self._request(10)  # below 50 ml
        self._request(400, required_by='2000-01-01')
        self.assertEqual(BloodRequest.objects.count(), 0)

    def test_patient_cannot_use_admin_or_donor_pages(self):
        for url in ['/admin-dashboard', '/admin-donor', '/admin-request', '/donor/donor-dashboard',
                    '/admin-camps', '/export/donors.csv']:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302, url)
            self.assertNotIn('/admin-dashboard', r['Location'] if 'admin' not in url else '')


class AdminPages(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.donor = make_donor()
        self.patient = make_patient()
        BloodDonate.objects.create(donor=self.donor, age=30, bloodgroup='O+', unit=300, status='Approved')
        BloodRequest.objects.create(request_by_patient=self.patient, patient_name='Pat', patient_age=40,
                                    reason='x', bloodgroup='O+', unit=100, priority='Emergency')
        self.client.login(username='boss', password=PW)

    def test_pages_render(self):
        for url in ['/admin-dashboard', '/admin-blood', '/admin-donor', '/admin-donor?q=dona&bloodgroup=O%2B',
                    '/admin-patient', '/admin-patient?q=pat', '/admin-request', '/admin-request-history',
                    '/admin-donation', '/admin-donation?status=Approved', '/admin-camps', '/find-donors',
                    '/notifications', f'/update-donor/{self.donor.id}', f'/update-patient/{self.patient.id}',
                    '/afterlogin']:
            r = self.client.get(url, follow=True)
            self.assertEqual(r.status_code, 200, url)

    def test_exports(self):
        for url, text in [('/export/donors.csv', 'Dona Tor'), ('/export/requests.csv', 'Emergency'),
                          ('/export/donations.csv', 'Approved')]:
            r = self.client.get(url)
            self.assertEqual(r['Content-Type'], 'text/csv')
            self.assertIn(text, r.content.decode())

    def test_stock_update(self):
        self.client.post('/admin-blood', {'bloodgroup': 'A+', 'unit': 1200})
        self.assertEqual(Stock.objects.get(bloodgroup='A+').unit, 1200)

    def test_camp_crud(self):
        d = (timezone.localdate() + timedelta(days=5)).isoformat()
        self.client.post('/admin-camps', {'title': 'Mega Camp', 'venue': 'Town Hall', 'city': 'Kochi',
                                          'date': d, 'start_time': '09:00', 'end_time': '14:00'})
        camp = Camp.objects.get()
        self.assertContains(self.client.get('/camps'), 'Mega Camp')
        self.client.post(f'/delete-camp/{camp.id}')
        self.assertEqual(Camp.objects.count(), 0)

    def test_update_and_delete_people(self):
        r = self.client.post(f'/update-donor/{self.donor.id}', {
            'first_name': 'New', 'last_name': 'Name', 'username': 'dono', 'new_password': '',
            'bloodgroup': 'O+', 'gender': '', 'address': 'Goa', 'mobile': '9876543210'})
        self.assertRedirects(r, '/admin-donor')
        self.assertEqual(User.objects.get(username='dono').first_name, 'New')
        self.assertTrue(User.objects.get(username='dono').check_password(PW))  # password kept
        self.client.post(f'/delete-donor/{self.donor.id}')
        self.assertFalse(Donor.objects.exists())
        self.client.post(f'/delete-patient/{self.patient.id}')
        self.assertFalse(Patient.objects.exists())

    def test_dashboard_has_alerts(self):
        r = self.client.get('/admin-dashboard')
        self.assertContains(r, 'emergency request')
        self.assertContains(r, 'Low stock alert')
