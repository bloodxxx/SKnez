from django.db import models
from django.contrib.auth.models import User
from apps.masters.models import Master


class Schedule(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_APPROVED = 'approved'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик'),
        (STATUS_APPROVED, 'Утверждено'),
    ]

    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='schedules', verbose_name='Мастер')
    date = models.DateField('Дата')
    start_time = models.TimeField('Начало работы')
    end_time = models.TimeField('Конец работы')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_schedules', verbose_name='Создал')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_schedules', verbose_name='Утвердил')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'
        unique_together = ('master', 'date')

    def __str__(self):
        return f"{self.master} — {self.date} ({self.start_time}–{self.end_time})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('Время начала должно быть меньше времени окончания')


class ScheduleLog(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='logs')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=200)
    details = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Лог расписания'
        verbose_name_plural = 'Логи расписания'
