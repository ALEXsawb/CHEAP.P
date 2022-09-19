from django.utils.http import urlsafe_base64_decode
from django.db.models.query import QuerySet
from online_store.models import Orders, OrderForm


__all__ = ['get_orders_number_by_email', 'get_orders_by_decoded_order_number']


def get_orders_by_specified_numbers(numbers_orders: list) -> QuerySet:
    return Orders.objects.filter(order_number__in=numbers_orders
                                 ).select_related('product', 'product__collection', 'product__type', 'order_number'
                                                  ).values('product__name', 'product__collection__name',
                                                           'product__type__type', 'color', 'size', 'quantity',
                                                           'order_number')


def get_email_by_orders_number(order_number: int) -> str:
    return OrderForm.objects.get(pk=order_number).email


def get_orders_number_by_email(user_email) -> QuerySet:
    try:
        return OrderForm.objects.filter(email=user_email).order_by('-date_create')[0].pk
    except:
        return None


def get_orders_by_decoded_order_number(**kwargs) -> list:
    order_number = int(urlsafe_base64_decode(kwargs['uidb64']))
    email_user = get_email_by_orders_number(order_number)
    return list(OrderForm.objects.filter(email=email_user).values_list('pk', flat=True))
