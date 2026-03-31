from django.db import models
from apps.bookings.models import Booking


class Payment(models.Model):
    METHOD_CASH = 'cash'
    METHOD_CARD = 'card'
    METHOD_CHOICES = [
        (METHOD_CASH, 'Наличные'),
        (METHOD_CARD, 'Безналичный'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment', verbose_name='Запись')
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    method = models.CharField('Способ оплаты', max_length=10, choices=METHOD_CHOICES)
    paid_at = models.DateTimeField('Дата оплаты', auto_now_add=True)
    notes = models.TextField('Примечание', blank=True)

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f"{self.booking} — {self.amount} \u20bd ({self.get_method_display()})"
