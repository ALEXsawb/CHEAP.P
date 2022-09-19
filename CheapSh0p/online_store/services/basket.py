from ast import literal_eval
from copy import deepcopy
from typing import Union
from online_store.models import Product
from .orders import get_orders_by_specified_numbers

__all__ = ['add_product_in_basket_or_update_data', 'get_basket_from_cookies', 'get_numbers_orders_from_cookies',
           'get_orders_by_numbers_orders', 'basket_formation', 'join_basket_with_formset_orders']


def add_product_in_basket_or_update_data(basket: dict, product: dict) -> dict:
    product_pk = product['product_id']
    product_color = product['add_color']
    product_size = product['add_size']

    def base_basket_product() -> dict:
        return {'color': product_color, 'size': product_size, 'quantity': 1}

    product_in_basket = basket.get(product_pk)
    if product_in_basket:
        for product_with_joint_id in product_in_basket:
            if product_with_joint_id['size'] == product_size and product_with_joint_id['color'] == product_color:
                product_with_joint_id['quantity'] += 1
                return basket
        product_in_basket.append(base_basket_product())
    else:
        basket[product_pk] = [base_basket_product(), ]
    return basket


def get_basket_from_cookies(request) -> dict:
    return _get_objects_from_cookies_by_name(request, 'basket')


def get_numbers_orders_from_cookies(request) -> list:
    return _get_objects_from_cookies_by_name(request, 'list_id_orders')


def _get_objects_from_cookies_by_name(request, objects_name: str) -> Union[list, dict]:
    try:
        return literal_eval(request.COOKIES[objects_name])
    except:
        if objects_name == 'basket':
            return {}
        return []


def get_orders_by_numbers_orders(numbers_orders: list) -> dict:
    dict_orders = {}
    orders = get_orders_by_specified_numbers(numbers_orders)
    for number_order in numbers_orders:
        order_list_with_common_order_number = []
        for order in orders:
            if order['order_number'] == number_order:
                order_list_with_common_order_number.append(order)
        if order_list_with_common_order_number:
            dict_orders[str(number_order)] = order_list_with_common_order_number
    return dict_orders


def basket_formation(basket_from_cookies: dict) -> list:
    """
    Получаем данные корзины из cookies. Получаем список id продуктов, которые являються ключами к данным по продуктам
    выбраных в корзину. Объеденяем этот список с списком форм заказа. Достаем данные по полученным ключам(id продуктов)
    и присваиваем экземпляру класса Product выбраному по id продукта(ключу корзины из кукис).
    """
    basket = []
    if basket_from_cookies:
        products = Product.objects.filter(pk__in=basket_from_cookies.keys()).select_related('collection')
        for product in products:
            for product_from_cookies in basket_from_cookies[str(product.pk)]:
                product_for_basket = deepcopy(product)
                product_for_basket.size = product_from_cookies['size']
                product_for_basket.color = product_from_cookies['color']
                product_for_basket.quantity = product_from_cookies['quantity']
                product_for_basket.total_price = product_for_basket.price * product_for_basket.quantity
                basket.append(product_for_basket)
    return basket


def join_basket_with_formset_orders(basket: list, formset_orders) -> list:
    for product_and_form_id in range(len(basket)):
        basket[product_and_form_id].form = formset_orders[product_and_form_id]
    return basket
