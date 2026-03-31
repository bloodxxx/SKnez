from django.urls import path
from . import views

urlpatterns = [
    path('', views.payments_list, name='payments_list'),
    path('create/<int:booking_pk>/', views.payment_create, name='payment_create'),
]
