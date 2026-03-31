from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book, name='book'),
    path('slots/', views.slots_partial, name='slots_partial'),
    path('masters-by-service/', views.masters_by_service, name='masters_by_service'),
    path('admin/list/', views.admin_bookings_list, name='admin_bookings_list'),
    path('admin/today/', views.admin_today, name='admin_today'),
    path('admin/<int:pk>/status/', views.booking_update_status, name='booking_update_status'),
]
