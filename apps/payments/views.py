from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Payment
from apps.bookings.models import Booking


@staff_member_required
def payments_list(request):
    payments = Payment.objects.select_related('booking__client', 'booking__master', 'booking__service').order_by('-paid_at')
    return render(request, 'admin_panel/payments_list.html', {'payments': payments})


@staff_member_required
def payment_create(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk)
    if hasattr(booking, 'payment'):
        messages.warning(request, 'Оплата для этой записи уже существует.')
        return redirect('admin_bookings_list')

    if request.method == 'POST':
        amount = request.POST.get('amount')
        method = request.POST.get('method')
        notes = request.POST.get('notes', '')
        if amount and method:
            Payment.objects.create(
                booking=booking,
                amount=amount,
                method=method,
                notes=notes,
            )
            booking.status = 'completed'
            booking.save()
            messages.success(request, 'Оплата зарегистрирована.')
            return redirect('admin_bookings_list')
    return render(request, 'admin_panel/payment_form.html', {
        'booking': booking,
        'method_choices': Payment.METHOD_CHOICES,
    })
