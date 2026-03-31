from django import forms
from .models import Schedule


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['master', 'date', 'start_time', 'end_time']
        widgets = {
            'master': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
        labels = {
            'master': 'Мастер',
            'date': 'Дата',
            'start_time': 'Начало работы',
            'end_time': 'Конец работы',
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        if start and end and start >= end:
            raise forms.ValidationError('Время начала должно быть раньше времени окончания.')
        return cleaned_data
