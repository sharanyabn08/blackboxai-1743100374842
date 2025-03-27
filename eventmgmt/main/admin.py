from django.contrib import admin
from .models import Event, Registration

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'organizer', 'price', 'capacity', 'is_active')
    list_filter = ('date', 'organizer', 'is_active')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'description', 'organizer')}),
        ('Event Details', {'fields': ('date', 'location', 'price', 'capacity')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'registration_date', 'payment_status', 'reminder_sent')
    list_filter = ('payment_status', 'reminder_sent', 'event')
    search_fields = ('user__username', 'event__title')
    readonly_fields = ('registration_date',)
    raw_id_fields = ('event', 'user')

admin.site.register(Event, EventAdmin)
admin.site.register(Registration, RegistrationAdmin)
