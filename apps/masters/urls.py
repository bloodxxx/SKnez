from django.urls import path
from . import views

urlpatterns = [
    path('', views.masters_list, name='masters_list_page'),
    path('services/', views.services_list, name='services_list_page'),
]
