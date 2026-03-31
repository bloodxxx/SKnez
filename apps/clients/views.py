from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from .models import Client
from .forms import ClientRegistrationForm, ClientProfileForm
from apps.masters.models import Master, Service


def home(request):
    services = Service.objects.filter(is_active=True)[:6]
    masters = Master.objects.filter(is_active=True)[:4]
    # One representative service per category for the feature cards
    categories_order = [c[0] for c in Service.CATEGORY_CHOICES]
    category_cards = []
    for cat in categories_order:
        svc = Service.objects.filter(is_active=True, category=cat).first()
        if svc:
            category_cards.append(svc)
    return render(request, 'client/home.html', {
        'services': services,
        'masters': masters,
        'category_cards': category_cards,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Добро пожаловать! Регистрация прошла успешно.')
            return redirect('home')
    else:
        form = ClientRegistrationForm()
    return render(request, 'client/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'client/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    try:
        client = request.user.client_profile
    except Client.DoesNotExist:
        client = None

    if request.method == 'POST' and client:
        form = ClientProfileForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    elif client:
        form = ClientProfileForm(instance=client)
    else:
        form = None

    bookings = []
    if client:
        bookings = client.bookings.select_related('master', 'service').order_by('-date', '-start_time')

    return render(request, 'client/profile.html', {
        'client': client,
        'form': form,
        'bookings': bookings,
    })


def services_list(request):
    selected_category = request.GET.get('category', '')
    qs = Service.objects.filter(is_active=True).order_by('category', 'name')
    if selected_category:
        qs = qs.filter(category=selected_category)
    categories = Service.CATEGORY_CHOICES
    return render(request, 'client/services_list.html', {
        'services': qs,
        'categories': categories,
        'selected_category': selected_category,
    })


def masters_list(request):
    from apps.masters.models import MasterService
    selected_service = request.GET.get('service', '')
    all_services = Service.objects.filter(is_active=True).order_by('category', 'name')

    filter_services = all_services.filter(pk=selected_service) if selected_service else all_services

    services_with_masters = []
    for service in filter_services:
        master_ids = MasterService.objects.filter(service=service).values_list('master_id', flat=True)
        masters = Master.objects.filter(id__in=master_ids, is_active=True)[:3]
        if masters:
            services_with_masters.append({'service': service, 'masters': masters})

    return render(request, 'client/masters_list.html', {
        'services_with_masters': services_with_masters,
        'all_services': all_services,
        'selected_service': selected_service,
    })
