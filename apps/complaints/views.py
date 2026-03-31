from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from .models import Complaint
from .forms import ComplaintForm, ComplaintResolveForm
from apps.clients.models import Client


@login_required
def complaint_form(request):
    try:
        client = request.user.client_profile
    except Client.DoesNotExist:
        messages.error(request, 'Профиль клиента не найден.')
        return redirect('profile')

    if request.method == 'POST':
        form = ComplaintForm(client=client, data=request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.client = client
            complaint.save()
            messages.success(request, 'Ваша жалоба принята. Мы рассмотрим её в ближайшее время.')
            return redirect('profile')
    else:
        form = ComplaintForm(client=client)
    return render(request, 'client/complaint_form.html', {'form': form})


@staff_member_required
def complaints_list(request):
    complaints = Complaint.objects.select_related('client', 'booking', 'handled_by').order_by('-created_at')

    status = request.GET.get('status')
    if status:
        complaints = complaints.filter(status=status)

    return render(request, 'admin_panel/complaints_list.html', {
        'complaints': complaints,
        'status_choices': Complaint.STATUS_CHOICES,
        'selected_status': status,
    })


@staff_member_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        form = ComplaintResolveForm(request.POST, instance=complaint)
        if form.is_valid():
            c = form.save(commit=False)
            c.handled_by = request.user
            if c.status == 'closed' and not c.closed_at:
                c.closed_at = timezone.now()
            c.save()
            messages.success(request, 'Жалоба обновлена.')
            return redirect('complaint_detail', pk=pk)
    else:
        form = ComplaintResolveForm(instance=complaint)
    return render(request, 'admin_panel/complaint_detail.html', {
        'complaint': complaint,
        'form': form,
    })
