from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Event, Registration
from accounts.models import CustomUser
from payments.models import Payment

def event_list(request):
    now = timezone.now()
    events = Event.objects.filter(is_active=True, date__gte=now).order_by('date')
    return render(request, 'main/event_list.html', {'events': events})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = Registration.objects.filter(
            event=event, 
            user=request.user
        ).exists()
    return render(request, 'main/event_detail.html', {
        'event': event,
        'is_registered': is_registered
    })

@login_required
def event_register(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    # Check if already registered
    if Registration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, 'You are already registered for this event')
        return redirect('event_detail', pk=event.pk)
    
    # Create registration
    registration = Registration.objects.create(
        event=event,
        user=request.user
    )
    
    # Send both confirmation and notification emails
    from .utils import send_attendee_confirmation, send_registration_notification
    try:
        send_attendee_confirmation(registration)
        send_registration_notification(registration)
    except Exception as e:
        # Log error but don't break registration flow
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending registration emails: {str(e)}")
    
    # Redirect to payment
    return redirect('create_checkout', registration_id=registration.id)

@login_required
def organizer_dashboard(request):
    if not request.user.is_organizer:
        messages.error(request, 'You do not have organizer privileges')
        return redirect('event_list')
        
    events = Event.objects.filter(organizer=request.user)
    registrations = Registration.objects.filter(event__in=events).select_related('event', 'user')
    
    return render(request, 'main/organizer_dashboard.html', {
        'events': events,
        'registrations': registrations,
        'upcoming_events_count': events.filter(date__gte=timezone.now()).count()
    })

@login_required
def event_registrations(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user:
        messages.error(request, 'You do not have permission to view these registrations')
        return redirect('event_detail', pk=event.pk)

    registrations = Registration.objects.filter(event=event).select_related('user')
    paid_count = registrations.filter(payment_status=True).count()
    pending_count = registrations.filter(payment_status=False).count()
    total_revenue = event.price * paid_count

    return render(request, 'main/event_registrations.html', {
        'event': event,
        'registrations': registrations,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'total_revenue': total_revenue
    })
