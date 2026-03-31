from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta, datetime
from .models import Schedule, ScheduleLog
from .forms import ScheduleForm
from apps.masters.models import Master


@staff_member_required
def schedule_list(request):
    schedules = Schedule.objects.select_related('master', 'created_by', 'approved_by').order_by('-date')
    all_masters = Master.objects.filter(is_active=True)

    selected_master = request.GET.get('master', '')
    selected_status = request.GET.get('status', '')

    if selected_master:
        schedules = schedules.filter(master_id=selected_master)
    if selected_status:
        schedules = schedules.filter(status=selected_status)

    return render(request, 'admin_panel/schedule_list.html', {
        'schedules': schedules,
        'all_masters': all_masters,
        'selected_master': selected_master,
        'selected_status': selected_status,
    })


@staff_member_required
def schedule_create(request):
    if request.method == 'POST':
        # Handle multiple dates (comma-separated from JS)
        dates_raw = request.POST.get('dates_list', '').strip()
        start_time_str = request.POST.get('start_time', '')
        end_time_str = request.POST.get('end_time', '')
        master_id = request.POST.get('master', '')

        if dates_raw:
            dates_list = [d.strip() for d in dates_raw.split(',') if d.strip()]
        else:
            # fallback to single date field
            single = request.POST.get('date', '')
            dates_list = [single] if single else []

        form = ScheduleForm(request.POST)
        errors = []
        created = 0

        if not master_id:
            errors.append('Выберите мастера.')
        if not dates_list:
            errors.append('Выберите хотя бы один день.')
        if not start_time_str or not end_time_str:
            errors.append('Укажите время работы.')

        if not errors:
            try:
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
            except ValueError:
                errors.append('Неверный формат времени.')

        if not errors:
            master = get_object_or_404(Master, pk=master_id)
            for date_str in dates_list:
                try:
                    schedule_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    continue
                # Skip if already exists
                if Schedule.objects.filter(master=master, date=schedule_date).exists():
                    messages.warning(request, f'Расписание для {master.full_name} на {schedule_date.strftime("%d.%m.%Y")} уже существует — пропущено.')
                    continue
                schedule = Schedule.objects.create(
                    master=master,
                    date=schedule_date,
                    start_time=start_time,
                    end_time=end_time,
                    created_by=request.user,
                    status='draft',
                )
                ScheduleLog.objects.create(
                    schedule=schedule,
                    changed_by=request.user,
                    action='Создано',
                    details=f'Расписание создано пользователем {request.user}'
                )
                created += 1
            if created:
                messages.success(request, f'Создано расписаний: {created}.')
            return redirect('schedule_list')
        else:
            for e in errors:
                messages.error(request, e)
    else:
        form = ScheduleForm()

    next_14_days = [date.today() + timedelta(days=i) for i in range(14)]
    masters = Master.objects.filter(is_active=True)
    return render(request, 'admin_panel/schedule_form.html', {
        'form': form,
        'title': 'Создать расписание',
        'next_14_days': next_14_days,
        'masters': masters,
    })


@staff_member_required
def schedule_edit(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            ScheduleLog.objects.create(
                schedule=schedule,
                changed_by=request.user,
                action='Изменено',
                details=f'Расписание изменено пользователем {request.user}'
            )
            messages.success(request, 'Расписание обновлено.')
            return redirect('schedule_list')
    else:
        form = ScheduleForm(instance=schedule)

    next_14_days = [date.today() + timedelta(days=i) for i in range(14)]
    masters = Master.objects.filter(is_active=True)
    return render(request, 'admin_panel/schedule_form.html', {
        'form': form,
        'schedule': schedule,
        'title': 'Редактировать расписание',
        'next_14_days': next_14_days,
        'masters': masters,
        'edit_date': schedule.date.strftime('%Y-%m-%d'),
    })


@staff_member_required
def schedule_approve(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if schedule.status == 'draft':
        schedule.status = 'approved'
        schedule.approved_by = request.user
        schedule.approved_at = timezone.now()
        schedule.save()
        ScheduleLog.objects.create(
            schedule=schedule,
            changed_by=request.user,
            action='Утверждено',
            details=f'Расписание утверждено пользователем {request.user}'
        )
        messages.success(request, 'Расписание утверждено.')
    return redirect('schedule_list')
