from django import forms
from .models import Complaint
from apps.bookings.models import Booking


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['booking', 'text']
        widgets = {
            'booking': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Опишите вашу жалобу подробно...'}),
        }
        labels = {
            'booking': 'Связанная запись (необязательно)',
            'text': 'Текст жалобы',
        }

    def __init__(self, client=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if client:
            self.fields['booking'].queryset = Booking.objects.filter(
                client=client, status='completed'
            ).select_related('master', 'service')
            self.fields['booking'].empty_label = '--- без привязки к записи ---'
        self.fields['booking'].required = False


class ComplaintResolveForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'resolution', 'admin_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'resolution': forms.Select(attrs={'class': 'form-select'}),
            'admin_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'status': 'Статус',
            'resolution': 'Решение',
            'admin_comment': 'Комментарий администратора',
        }
