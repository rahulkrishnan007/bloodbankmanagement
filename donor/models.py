from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
BLOOD_GROUP_CHOICES = [(b, b) for b in BLOOD_GROUPS]


class Donor(models.Model):
    GENDERS = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/Donor/', null=True, blank=True)

    bloodgroup = models.CharField(max_length=10)

    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=False)

    # --- new ---
    gender = models.CharField(max_length=10, choices=GENDERS, blank=True, default='')
    weight = models.PositiveIntegerField(null=True, blank=True, help_text='Weight in kg')
    is_available = models.BooleanField(default=True, help_text='Visible in the "Find Donors" search')

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.user.first_name

    # ---------- donation statistics / eligibility ----------
    @property
    def approved_donations(self):
        return self.blooddonate_set.filter(status='Approved')

    @property
    def total_donations(self):
        return self.approved_donations.count()

    @property
    def total_units(self):
        return self.approved_donations.aggregate(t=models.Sum('unit'))['t'] or 0

    @property
    def lives_saved(self):
        # one donation can help up to three patients
        return self.total_donations * 3

    @property
    def last_donation_date(self):
        last = self.approved_donations.order_by('-date').first()
        return last.date if last else None

    @property
    def next_eligible_date(self):
        last = self.last_donation_date
        if not last:
            return None
        return last + timedelta(days=settings.DONATION_GAP_DAYS)

    @property
    def is_eligible(self):
        nxt = self.next_eligible_date
        return nxt is None or nxt <= timezone.localdate()

    @property
    def days_to_eligible(self):
        nxt = self.next_eligible_date
        if nxt is None:
            return 0
        return max((nxt - timezone.localdate()).days, 0)

    @property
    def badge(self):
        n = self.total_donations
        if n >= 10:
            return ('Platinum Hero', 'platinum')
        if n >= 5:
            return ('Gold Donor', 'gold')
        if n >= 2:
            return ('Silver Donor', 'silver')
        if n >= 1:
            return ('Bronze Donor', 'bronze')
        return ('New Donor', 'new')


class BloodDonate(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    disease = models.CharField(max_length=100, default="Nothing")
    age = models.PositiveIntegerField()
    bloodgroup = models.CharField(max_length=10)
    unit = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default="Pending")
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.donor} - {self.bloodgroup} - {self.unit}ml"
