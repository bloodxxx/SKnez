from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.complaint_form, name='complaint_form'),
    path('admin/list/', views.complaints_list, name='complaints_list'),
    path('admin/<int:pk>/', views.complaint_detail, name='complaint_detail'),
]
