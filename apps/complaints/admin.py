from django.contrib import admin
from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['client', 'status', 'resolution', 'created_at', 'closed_at', 'is_overdue']
    list_filter = ['status', 'resolution']
    search_fields = ['client__full_name', 'text']
    readonly_fields = ['created_at']
