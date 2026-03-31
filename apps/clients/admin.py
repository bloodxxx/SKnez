from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'created_at', 'visit_count']
    search_fields = ['full_name', 'phone', 'email']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
