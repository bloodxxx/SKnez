from django.urls import path
from . import views

urlpatterns = [
    path('kpi/', views.kpi_dashboard, name='kpi_dashboard'),
]
