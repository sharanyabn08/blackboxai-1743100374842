from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('registration', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('registration__event__title', 'registration__user__username')
    readonly_fields = ('created_at', 'updated_at', 'stripe_payment_intent_id')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('registration', 'amount', 'status')
        }),
        ('Stripe Details', {
            'fields': ('stripe_payment_intent_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Payment, PaymentAdmin)
