from django.contrib import admin

from .models import BloodDonate, Donor

admin.site.register(Donor)


@admin.register(BloodDonate)
class BloodDonateAdmin(admin.ModelAdmin):
    list_display = ('donor', 'bloodgroup', 'unit', 'status', 'date')
    list_filter = ('status', 'bloodgroup')
