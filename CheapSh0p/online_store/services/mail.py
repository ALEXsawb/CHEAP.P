from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_reset_mail(request, user_email: str, order_number: int) -> None:
    context = {'email': user_email,
               'domain': get_current_site(request).domain,
               'uid': urlsafe_base64_encode(force_bytes(order_number)), }
    message_for_email = render_to_string('online_store/auth_by_email.html', context=context)
    send_mail(subject='Востановление доступа к уже оформленным заказам', message=message_for_email,
              recipient_list=(user_email,), from_email='cheappsh0p333@gmail.com', fail_silently=False)