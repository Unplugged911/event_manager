from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('statistics/', views.event_statistics, name='event_statistics'),  # Без event_id
    path('statistics/<int:event_id>/', views.event_statistics, name='event_statistics_by_event'),  # С event_id
]