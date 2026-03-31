from django.shortcuts import render
from .models import Master, Service, MasterService


def masters_list(request):
    services = Service.objects.filter(is_active=True)
    services_with_masters = []
    for service in services:
        master_ids = MasterService.objects.filter(service=service).values_list('master_id', flat=True)
        masters = Master.objects.filter(id__in=master_ids, is_active=True)[:3]
        if masters:
            services_with_masters.append({'service': service, 'masters': masters})
    return render(request, 'client/masters_list.html', {'services_with_masters': services_with_masters})


def services_list(request):
    services = Service.objects.filter(is_active=True).order_by('name')
    return render(request, 'client/services_list.html', {'services': services})
