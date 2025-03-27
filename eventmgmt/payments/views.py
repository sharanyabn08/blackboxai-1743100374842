import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from main.models import Registration
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': settings.STRIPE_CURRENCY,
                    'product_data': {
                        'name': registration.event.title,
                    },
                    'unit_amount': int(registration.event.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('payment_success')
            ) + f'?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=request.build_absolute_uri(
                reverse('payment_cancel')
            ),
            metadata={
                'registration_id': registration.id
            }
        )
        
        # Create payment record
        Payment.objects.create(
            registration=registration,
            amount=registration.event.price,
            stripe_payment_intent_id=checkout_session.payment_intent,
            status='pending'
        )
        
        return redirect(checkout_session.url)
    except Exception as e:
        return JsonResponse({'error': str(e)})

def payment_success(request):
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            payment = Payment.objects.get(
                stripe_payment_intent_id=session.payment_intent
            )
            payment.status = 'succeeded'
            payment.save()
            
            # Update registration payment status
            registration = payment.registration
            registration.payment_status = True
            registration.save()
            
            return render(request, 'payments/success.html')
        except Exception as e:
            return JsonResponse({'error': str(e)})
    return redirect('home')

def payment_cancel(request):
    return render(request, 'payments/cancel.html')

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_payment_success(session)

    return HttpResponse(status=200)

def handle_payment_success(session):
    registration_id = session.metadata.get('registration_id')
    if registration_id:
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=session.payment_intent
            )
            payment.status = 'succeeded'
            payment.save()
            
            registration = payment.registration
            registration.payment_status = True
            registration.save()
        except Payment.DoesNotExist:
            pass
