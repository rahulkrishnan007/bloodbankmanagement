from django.contrib import admin

from .models import BloodRequest, Camp, Notification, Stock

admin.site.register(Stock)
admin.site.register(Camp)
admin.site.register(Notification)


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'bloodgroup', 'unit', 'priority', 'status', 'date')
    list_filter = ('status', 'priority', 'bloodgroup')
