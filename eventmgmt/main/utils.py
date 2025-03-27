from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_attendee_confirmation(registration):
    """
    Send confirmation email to attendee after registration.
    Includes both HTML and plain text versions.
    """
    event = registration.event
    subject = f'Registration Confirmation for {event.title}'
    
    context = {
        'event': event,
        'registration': registration,
        'protocol': 'https',
        'domain': getattr(settings, 'DOMAIN', 'localhost')
    }

    try:
        text_content = render_to_string('emails/attendee_confirmation.txt', context)
        html_content = render_to_string('emails/attendee_confirmation.html', context)
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [registration.user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
    except Exception as e:
        logger.error(f"Failed to send attendee confirmation email: {str(e)}")
        if settings.DEBUG:
            raise

def send_registration_notification(registration):
    """
    Send email notification to organizer about new registration.
    Includes both HTML and plain text versions.
    """
    event = registration.event
    subject = f'New registration for {event.title}'
    
    context = {
        'event': event,
        'registration': registration,
        'protocol': 'https',
        'domain': getattr(settings, 'DOMAIN', 'localhost')
    }

    try:
        # Render both text and HTML versions
        text_content = render_to_string('emails/registration_notification.txt', context)
        html_content = render_to_string('emails/registration_notification.html', context)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [event.organizer.email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send(fail_silently=False)
        
    except Exception as e:
        logger.error(f"Failed to send registration email: {str(e)}")
        if settings.DEBUG:
            raise  # Re-raise in development for debugging
