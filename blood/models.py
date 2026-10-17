from django.contrib.auth.models import User
from django.db import models

from donor import models as dmodels
from patient import models as pmodels


class Stock(models.Model):
    bloodgroup = models.CharField(max_length=10)
    unit = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.bloodgroup


class BloodRequest(models.Model):
    PRIORITIES = [('Normal', 'Normal'), ('Urgent', 'Urgent'), ('Emergency', 'Emergency')]

    request_by_patient = models.ForeignKey(pmodels.Patient, null=True, on_delete=models.CASCADE)
    request_by_donor = models.ForeignKey(dmodels.Donor, null=True, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=30)
    patient_age = models.PositiveIntegerField()
    reason = models.CharField(max_length=500)
    bloodgroup = models.CharField(max_length=10)
    unit = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, default="Pending")
    date = models.DateField(auto_now_add=True)

    # --- new ---
    priority = models.CharField(max_length=10, choices=PRIORITIES, default='Normal')
    hospital = models.CharField(max_length=100, blank=True, default='')
    required_by = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.bloodgroup

    @property
    def requester(self):
        return self.request_by_patient or self.request_by_donor

    @property
    def requester_user(self):
        r = self.requester
        return r.user if r else None


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    level = models.CharField(max_length=10, default='info')   # info / success / danger
    link = models.CharField(max_length=200, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.user.username}: {self.message}"


class Camp(models.Model):
    title = models.CharField(max_length=120)
    venue = models.CharField(max_length=200)
    city = models.CharField(max_length=60)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    organizer = models.CharField(max_length=100, blank=True, default='')
    contact = models.CharField(max_length=30, blank=True, default='')
    description = models.TextField(blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.title} ({self.date})"
