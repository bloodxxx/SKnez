from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'method', 'paid_at']
    list_filter = ['method', 'paid_at']
    search_fields = ['booking__client__full_name']
