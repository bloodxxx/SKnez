from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Count, Sum, Q
import datetime

from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.clients.models import Client
from apps.masters.models import Master
from apps.complaints.models import Complaint


@staff_member_required
def kpi_dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)

    # статистика сегодняшнего дня
    today_bookings = Booking.objects.filter(date=today)
    today_count = today_bookings.count()
    today_completed = today_bookings.filter(status='completed').count()
    today_cancelled = today_bookings.filter(status='cancelled').count()

    # месячная статистика
    month_bookings = Booking.objects.filter(date__gte=month_start)
    month_count = month_bookings.count()
    month_completed = month_bookings.filter(status='completed').count()

    # доходы
    month_revenue = Payment.objects.filter(
        paid_at__date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or 0

    today_revenue = Payment.objects.filter(
        paid_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0

    # клиенты
    total_clients = Client.objects.count()
    new_clients_month = Client.objects.filter(created_at__date__gte=month_start).count()

    # заказы
    open_complaints = Complaint.objects.filter(status__in=['new', 'in_progress']).count()
    overdue_complaints = sum(1 for c in Complaint.objects.filter(status__in=['new', 'in_progress']) if c.is_overdue)

    # мастера
    active_masters = Master.objects.filter(is_active=True).count()

    # топ мастеров по количеству выполненных заказов за месяц
    top_masters = (
        Booking.objects
        .filter(date__gte=month_start, status='completed')
        .values('master__full_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    # Recent bookings
    recent_bookings = Booking.objects.select_related('client', 'master', 'service').order_by('-created_at')[:10]

    context = {
        'today': today,
        'today_count': today_count,
        'today_completed': today_completed,
        'today_cancelled': today_cancelled,
        'today_revenue': today_revenue,
        'month_count': month_count,
        'month_completed': month_completed,
        'month_revenue': month_revenue,
        'total_clients': total_clients,
        'new_clients_month': new_clients_month,
        'open_complaints': open_complaints,
        'overdue_complaints': overdue_complaints,
        'active_masters': active_masters,
        'top_masters': top_masters,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'dashboard/kpi.html', context)
