from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import datetime
from datetime import date, timedelta

from .models import Booking
from .forms import BookingForm, BookingStatusForm
from apps.clients.models import Client
from apps.masters.models import Master, Service, MasterService
from apps.schedule.models import Schedule


def get_available_slots(master, date, service):
    """Return list of available time slots for a master on a given date."""
    try:
        schedule = Schedule.objects.get(master=master, date=date, status='approved')
    except Schedule.DoesNotExist:
        return []

    duration = service.duration_minutes
    start = datetime.datetime.combine(date, schedule.start_time)
    end = datetime.datetime.combine(date, schedule.end_time)

    # Get existing bookings for this master on this date
    existing = Booking.objects.filter(
        master=master,
        date=date,
        status__in=['pending', 'confirmed', 'arrived']
    ).values_list('start_time', 'end_time')

    slots = []
    current = start
    while current + datetime.timedelta(minutes=duration) <= end:
        slot_end = current + datetime.timedelta(minutes=duration)
        # Check for conflicts
        conflict = False
        for b_start, b_end in existing:
            b_start_dt = datetime.datetime.combine(date, b_start)
            b_end_dt = datetime.datetime.combine(date, b_end)
            if not (slot_end <= b_start_dt or current >= b_end_dt):
                conflict = True
                break
        if not conflict:
            slots.append(current.time())
        current += datetime.timedelta(minutes=30)
    return slots


def slots_partial(request):
    """HTMX partial: returns available slots for a given master/service/date."""
    master_id = request.GET.get('master')
    service_id = request.GET.get('service')
    date_str = request.GET.get('date')

    slots = []
    error = ''

    if master_id and service_id and date_str:
        try:
            master = Master.objects.get(pk=master_id)
            service = Service.objects.get(pk=service_id)
            date = datetime.date.fromisoformat(date_str)
            if date < datetime.date.today():
                error = 'Выберите будущую дату.'
            else:
                slots = get_available_slots(master, date, service)
                if not slots:
                    error = 'Нет доступных слотов на выбранную дату.'
        except (Master.DoesNotExist, Service.DoesNotExist, ValueError):
            error = 'Неверные данные.'

    return render(request, 'client/slots_partial.html', {'slots': slots, 'error': error})


def book(request):
    # Determine client (authenticated) or guest
    client = None
    if request.user.is_authenticated:
        try:
            client = request.user.client_profile
        except Client.DoesNotExist:
            pass

    # Pre-select service from GET param
    selected_service_id = request.GET.get('service', '')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        selected_service_id = request.POST.get('service', selected_service_id)

        # Guest fields validation
        guest_name = request.POST.get('guest_name', '').strip()
        guest_phone = request.POST.get('guest_phone', '').strip()
        guest_errors = {}
        if not client:
            if not guest_name:
                guest_errors['guest_name'] = 'Пожалуйста, введите ваше имя.'
            if not guest_phone:
                guest_errors['guest_phone'] = 'Пожалуйста, введите номер телефона.'

        if form.is_valid() and not guest_errors:
            booking_master = form.cleaned_data['master']
            booking_service = form.cleaned_data['service']
            booking_date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            notes = form.cleaned_data.get('notes', '')

            with transaction.atomic():
                # Lock relevant bookings
                conflicts = Booking.objects.select_for_update().filter(
                    master=booking_master,
                    date=booking_date,
                    status__in=['pending', 'confirmed', 'arrived'],
                    start_time__lt=end_time,
                    end_time__gt=start_time,
                )
                if conflicts.exists():
                    messages.error(request, 'К сожалению, это время уже занято. Пожалуйста, выберите другое.')
                    return redirect('book')

                booking = Booking.objects.create(
                    client=client,
                    guest_name=guest_name if not client else '',
                    guest_phone=guest_phone if not client else '',
                    master=booking_master,
                    service=booking_service,
                    date=booking_date,
                    start_time=start_time,
                    end_time=end_time,
                    notes=notes,
                    status='pending',
                )
            messages.success(request, f'Заявка принята на {booking_date} в {start_time.strftime("%H:%M")}. Ожидайте звонка для подтверждения.')
            if client:
                return redirect('profile')
            else:
                return redirect('home')
    else:
        guest_errors = {}
        initial = {}
        if selected_service_id:
            initial['service'] = selected_service_id
        form = BookingForm(initial=initial)

    today = date.today()
    next_7_days = [today + timedelta(days=i) for i in range(7)]
    masters = Master.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True).order_by('category', 'name')

    # Group services by category
    categories_order = [c[0] for c in Service.CATEGORY_CHOICES]
    categories_labels = dict(Service.CATEGORY_CHOICES)
    services_by_category = []
    for cat_key in categories_order:
        cat_services = [s for s in services if s.category == cat_key]
        if cat_services:
            services_by_category.append({
                'key': cat_key,
                'label': categories_labels[cat_key],
                'services': cat_services,
            })

    # Pre-load masters for pre-selected service (server-side, no HTMX timing issues)
    effective_service_id = selected_service_id or (form.data.get('service') if request.method == 'POST' else '')
    initial_masters = []
    if effective_service_id:
        try:
            master_ids = MasterService.objects.filter(
                service_id=effective_service_id
            ).values_list('master_id', flat=True)
            initial_masters = list(Master.objects.filter(id__in=master_ids, is_active=True))
        except Exception:
            pass

    return render(request, 'client/book.html', {
        'form': form,
        'masters': masters,
        'services': services,
        'services_by_category': services_by_category,
        'today': today,
        'next_7_days': next_7_days,
        'selected_service_id': effective_service_id,
        'initial_masters': initial_masters,
        'is_guest': not client,
        'guest_errors': guest_errors,
        'guest_name_val': request.POST.get('guest_name', '') if request.method == 'POST' else '',
        'guest_phone_val': request.POST.get('guest_phone', '') if request.method == 'POST' else '',
    })


def masters_by_service(request):
    """HTMX partial: returns master cards for a given service."""
    service_id = request.GET.get('service')
    masters = []
    if service_id:
        master_ids = MasterService.objects.filter(
            service_id=service_id
        ).values_list('master_id', flat=True)
        masters = Master.objects.filter(id__in=master_ids, is_active=True)

    html = ''
    if masters:
        html = '<div class="master-cards-grid">'
        for master in masters:
            initial = master.full_name[0] if master.full_name else '?'
            if master.photo:
                photo_html = f'<img src="{master.photo.url}" alt="{master.full_name}">'
            else:
                photo_html = f'<span style="font-size:1.8rem;font-weight:700;">{initial}</span>'
            html += f'''
            <div class="master-card" onclick="selectMaster({master.pk}, this)">
                <div class="master-photo">{photo_html}</div>
                <div class="master-name">{master.full_name}</div>
                <div class="master-spec">{master.specialization}</div>
            </div>'''
        html += '</div>'
    else:
        html = '<p class="text-muted small"><i class="bi bi-info-circle me-1"></i>Мастера для этой услуги не найдены</p>'

    return HttpResponse(html)


# --- Admin views ---

@staff_member_required
def admin_bookings_list(request):
    bookings = Booking.objects.select_related('client', 'master', 'service').order_by('-date', '-start_time')

    # Filters
    status = request.GET.get('status')
    master_id = request.GET.get('master')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if status:
        bookings = bookings.filter(status=status)
    if master_id:
        bookings = bookings.filter(master_id=master_id)
    if date_from:
        bookings = bookings.filter(date__gte=date_from)
    if date_to:
        bookings = bookings.filter(date__lte=date_to)

    masters = Master.objects.filter(is_active=True)
    return render(request, 'admin_panel/bookings_list.html', {
        'bookings': bookings,
        'masters': masters,
        'status_choices': Booking.STATUS_CHOICES,
        'selected_status': status,
        'selected_master': master_id,
        'date_from': date_from,
        'date_to': date_to,
    })


@staff_member_required
def admin_today(request):
    today = timezone.localdate()
    bookings = Booking.objects.filter(date=today).select_related('client', 'master', 'service').order_by('start_time')
    return render(request, 'admin_panel/today.html', {
        'bookings': bookings,
        'today': today,
    })


@staff_member_required
def booking_update_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingStatusForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статус записи обновлён.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_today'))
