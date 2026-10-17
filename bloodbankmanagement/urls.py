"""URL configuration for the Blood Bank Management System."""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path, re_path
from django.views.static import serve

from blood import views
from blood.auth_views import RoleLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('donor/', include('donor.urls')),
    path('patient/', include('patient.urls')),

    path('', views.home_view, name='home'),
    path('compatibility', views.compatibility_view, name='compatibility'),
    path('camps', views.camps_view, name='camps'),
    path('find-donors', views.find_donors_view, name='find-donors'),
    path('notifications', views.notifications_view, name='notifications'),
    path('notifications/read', views.notifications_read_view, name='notifications-read'),
    path('cancel-request/<int:pk>', views.cancel_request_view, name='cancel-request'),

    path('logout', LogoutView.as_view(template_name='blood/logout.html'), name='logout'),
    path('afterlogin', views.afterlogin_view, name='afterlogin'),
    path('adminlogin', RoleLoginView.as_view(template_name='blood/adminlogin.html'), name='adminlogin'),

    path('admin-dashboard', views.admin_dashboard_view, name='admin-dashboard'),
    path('admin-blood', views.admin_blood_view, name='admin-blood'),
    path('admin-donor', views.admin_donor_view, name='admin-donor'),
    path('admin-patient', views.admin_patient_view, name='admin-patient'),
    path('update-donor/<int:pk>', views.update_donor_view, name='update-donor'),
    path('delete-donor/<int:pk>', views.delete_donor_view, name='delete-donor'),
    path('update-patient/<int:pk>', views.update_patient_view, name='update-patient'),
    path('delete-patient/<int:pk>', views.delete_patient_view, name='delete-patient'),
    path('admin-request', views.admin_request_view, name='admin-request'),
    path('admin-request-history', views.admin_request_history_view, name='admin-request-history'),
    path('admin-donation', views.admin_donation_view, name='admin-donation'),
    path('approve-donation/<int:pk>', views.approve_donation_view, name='approve-donation'),
    path('reject-donation/<int:pk>', views.reject_donation_view, name='reject-donation'),
    path('update-approve-status/<int:pk>', views.update_approve_status_view, name='update-approve-status'),
    path('update-reject-status/<int:pk>', views.update_reject_status_view, name='update-reject-status'),
    path('admin-camps', views.admin_camps_view, name='admin-camps'),
    path('delete-camp/<int:pk>', views.delete_camp_view, name='delete-camp'),
    path('export/donors.csv', views.export_donors_view, name='export-donors'),
    path('export/requests.csv', views.export_requests_view, name='export-requests'),
    path('export/donations.csv', views.export_donations_view, name='export-donations'),

    # uploaded profile photos
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
