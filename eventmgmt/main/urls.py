from django.urls import path
from . import views
from .export_views import export_registrations_csv

app_name = 'main'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/register/', views.event_register, name='event_register'),
    path('dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/registrations/', views.event_registrations, name='event_registrations'),
    path('events/<int:pk>/export/', export_registrations_csv, name='export_registrations'),
]
