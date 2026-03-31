from django.contrib import admin
from django.utils import timezone
from .models import Schedule, ScheduleLog


class ScheduleLogInline(admin.TabularInline):
    model = ScheduleLog
    extra = 0
    readonly_fields = ['changed_by', 'changed_at', 'action', 'details']
    can_delete = False


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['master', 'date', 'start_time', 'end_time', 'status']
    list_filter = ['status', 'date', 'master']
    search_fields = ['master__full_name']
    inlines = [ScheduleLogInline]
    actions = ['approve_schedules']

    def approve_schedules(self, request, queryset):
        for schedule in queryset.filter(status='draft'):
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
        self.message_user(request, "Расписания утверждены")
    approve_schedules.short_description = "Утвердить расписание"
