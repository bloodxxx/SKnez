from django.db import models
from django.utils import timezone
from apps.clients.models import Client
from apps.bookings.models import Booking
from django.contrib.auth.models import User


class Complaint(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'В работе'),
        (STATUS_CLOSED, 'Закрыта'),
    ]

    RESOLUTION_REFUSAL = 'refusal'
    RESOLUTION_COMPENSATION = 'compensation'
    RESOLUTION_CHOICES = [
        (RESOLUTION_REFUSAL, 'Отказ'),
        (RESOLUTION_COMPENSATION, 'Компенсация'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='complaints', verbose_name='Клиент')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints', verbose_name='Запись')
    text = models.TextField('Текст жалобы')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    resolution = models.CharField('Решение', max_length=20, choices=RESOLUTION_CHOICES, null=True, blank=True)
    admin_comment = models.TextField('Комментарий администратора', blank=True)
    created_at = models.DateTimeField('Дата подачи', auto_now_add=True)
    closed_at = models.DateTimeField('Дата закрытия', null=True, blank=True)
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Обработал')

    class Meta:
        verbose_name = 'Жалоба'
        verbose_name_plural = 'Жалобы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Жалоба #{self.pk} от {self.client}"

    @property
    def is_overdue(self):
        if self.status != self.STATUS_CLOSED:
            from datetime import timedelta
            deadline = self.created_at + timedelta(days=1)
            return timezone.now() > deadline
        return False
