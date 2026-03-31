from django.contrib import admin
from .models import Master, Service, MasterService


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'duration_minutes', 'price', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['name']
    fields = ['name', 'category', 'photo', 'duration_minutes', 'price', 'description', 'is_active']


class MasterServiceInline(admin.TabularInline):
    model = MasterService
    extra = 1


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialization', 'is_active']
    list_filter = ['is_active', 'specialization']
    search_fields = ['full_name', 'specialization']
    inlines = [MasterServiceInline]
