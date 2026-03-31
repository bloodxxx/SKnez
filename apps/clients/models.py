from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile', null=True, blank=True)
    full_name = models.CharField('ФИО', max_length=200)
    phone = models.CharField('Телефон', max_length=20, unique=True)
    email = models.EmailField('Email', blank=True, null=True)
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    notes = models.TextField('Заметки', blank=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    def visit_count(self):
        return self.bookings.filter(status='completed').count()
    visit_count.short_description = 'Визитов'
