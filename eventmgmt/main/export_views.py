from django.http import HttpResponse
import csv
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Event, Registration

@login_required
def export_registrations_csv(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.organizer != request.user:
        return HttpResponse('Unauthorized', status=401)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{event.slug}_registrations.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Registration Date', 'Payment Status', 'Amount'])

    registrations = Registration.objects.filter(event=event).select_related('user')
    for reg in registrations:
        writer.writerow([
            reg.user.username,
            reg.user.email,
            reg.registration_date.strftime("%Y-%m-%d %H:%M"),
            'Paid' if reg.payment_status else 'Pending',
            str(event.price) if reg.payment_status else '0'
        ])

    return response