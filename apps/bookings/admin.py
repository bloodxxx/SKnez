from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['client', 'master', 'service', 'date', 'start_time', 'status']
    list_filter = ['status', 'date', 'master']
    search_fields = ['client__full_name', 'client__phone', 'master__full_name']
    date_hierarchy = 'date'
