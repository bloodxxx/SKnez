from django.db import models
from apps.clients.models import Client
from apps.masters.models import Master, Service


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_ARRIVED = 'arrived'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_NO_SHOW = 'no_show'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает подтверждения'),
        (STATUS_CONFIRMED, 'Подтверждено'),
        (STATUS_ARRIVED, 'Клиент пришёл'),
        (STATUS_COMPLETED, 'Выполнено'),
        (STATUS_CANCELLED, 'Отменено'),
        (STATUS_NO_SHOW, 'Не явился'),
    ]

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings', verbose_name='Клиент')
    guest_name = models.CharField('Имя гостя', max_length=100, blank=True)
    guest_phone = models.CharField('Телефон гостя', max_length=20, blank=True)
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='bookings', verbose_name='Мастер')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')
    date = models.DateField('Дата')
    start_time = models.TimeField('Время начала')
    end_time = models.TimeField('Время окончания')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField('Примечания клиента', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.client} \u2192 {self.master} | {self.date} {self.start_time}"
