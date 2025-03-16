from django.contrib import admin
from .models import Event, Participant

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('type', 'date', 'location', 'participants_count')

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'event')