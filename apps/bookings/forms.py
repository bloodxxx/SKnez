from django import forms
from .models import Booking
from apps.masters.models import Master, Service
import datetime


class BookingForm(forms.ModelForm):
    date = forms.DateField(
        label='Дата',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%Y-%m-%d'],
    )
    master = forms.ModelChoiceField(
        queryset=Master.objects.filter(is_active=True),
        label='Мастер',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_master'}),
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.filter(is_active=True),
        label='Услуга',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_service'}),
    )
    start_time = forms.TimeField(
        label='Время',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_start_time'}),
        required=False,
    )
    notes = forms.CharField(
        label='Пожелания',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Любые пожелания или примечания...'}),
    )

    class Meta:
        model = Booking
        fields = ['master', 'service', 'date', 'start_time', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'].widget = forms.Select(
            choices=[('', '--- выберите время ---')],
            attrs={'class': 'form-select'}
        )

    def clean(self):
        cleaned_data = super().clean()
        master = cleaned_data.get('master')
        service = cleaned_data.get('service')
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')

        if not start_time:
            self.add_error('start_time', 'Пожалуйста, выберите время.')
            return cleaned_data

        if master and service and date and start_time:
            # Check for date in the past
            if date < datetime.date.today():
                self.add_error('date', 'Нельзя записаться на прошедшую дату.')

            # Calculate end time
            duration = service.duration_minutes
            start_dt = datetime.datetime.combine(date, start_time)
            end_dt = start_dt + datetime.timedelta(minutes=duration)
            cleaned_data['end_time'] = end_dt.time()

        return cleaned_data


class BookingStatusForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'status': 'Статус',
        }
