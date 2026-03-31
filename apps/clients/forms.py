from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Client


class ClientRegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        label='ФИО',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванова Мария Ивановна'})
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'})
    )
    email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.ru'})
    )

    class Meta:
        model = User
        fields = ('username', 'full_name', 'phone', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].label = 'Подтверждение пароля'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            Client.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                phone=self.cleaned_data['phone'],
                email=self.cleaned_data.get('email', ''),
            )
        return user


class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['full_name', 'phone', 'email', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'full_name': 'ФИО',
            'phone': 'Телефон',
            'email': 'Email',
            'notes': 'Заметки',
        }
