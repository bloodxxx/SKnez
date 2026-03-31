from django.db import models


class Service(models.Model):
    CATEGORY_MANICURE = 'manicure'
    CATEGORY_HAIR = 'hair'
    CATEGORY_SKIN = 'skin'
    CATEGORY_BROWS = 'brows'
    CATEGORY_MAKEUP = 'makeup'
    CATEGORY_OTHER = 'other'

    CATEGORY_CHOICES = [
        (CATEGORY_MANICURE, 'Маникюр и педикюр'),
        (CATEGORY_HAIR, 'Волосы'),
        (CATEGORY_SKIN, 'Уход за кожей'),
        (CATEGORY_BROWS, 'Брови и ресницы'),
        (CATEGORY_MAKEUP, 'Макияж'),
        (CATEGORY_OTHER, 'Другое'),
    ]

    name = models.CharField('Название услуги', max_length=200)
    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    photo = models.ImageField('Фото услуги', upload_to='services/', blank=True, null=True)
    duration_minutes = models.PositiveIntegerField('Длительность (мин)')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    description = models.TextField('Описание', blank=True)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return f"{self.name} ({self.duration_minutes} мин, {self.price} \u20bd)"


class Master(models.Model):
    full_name = models.CharField('ФИО', max_length=200)
    specialization = models.CharField('Специализация', max_length=200)
    photo = models.ImageField('Фото', upload_to='masters/', blank=True, null=True)
    services = models.ManyToManyField(Service, through='MasterService', verbose_name='Услуги')
    bio = models.TextField('О мастере', blank=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'

    def __str__(self):
        return self.full_name


class MasterService(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, verbose_name='Мастер')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')

    class Meta:
        verbose_name = 'Услуга мастера'
        verbose_name_plural = 'Услуги мастеров'
        unique_together = ('master', 'service')

    def __str__(self):
        return f"{self.master} — {self.service}"
