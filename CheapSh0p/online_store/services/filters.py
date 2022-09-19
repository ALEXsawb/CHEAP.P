from ast import literal_eval
from typing import Union, Tuple, List
from django.db.models import Q

from online_store.services import collections, products


__all__ = ['FilteringError', 'get_context_by_filter', ]


def get_price(max_or_min: str, request_dict) -> str:
    price = request_dict.pop(f'{max_or_min}_price')
    return float(price[0]) if isinstance(price, list) else price


def get_filters_for_pagination_and_active_filter(request_dict) -> Tuple[dict, list]:
    request_dict.pop('csrfmiddlewaretoken', None)
    filters = request_dict.pop('filters', None)
    if not filters:
        filters = {'type': [], 'sort_by': [], 'collection': [], 'size': [], 'color': []}
        active_filter_categories = list(request_dict.keys())
        for fltr in active_filter_categories:
            filter_name, filter_value = fltr.split('__')
            filters[filter_name].append(filter_value)
    else:
        filters = literal_eval(filters[0])
        active_filter_categories = literal_eval(request_dict.pop('act_filters')[0])
    return filters, active_filter_categories


def get_order_by(filters: dict) -> list:
    if filters['sort_by']:
        order_by = []
        sort_fields = {'increasing_price': 'price', 'filling_price': '-price', 'popular': '-views',
                       'recent': '-pk'}
        for sort_name in filters['sort_by']:
            order_by.append(sort_fields[sort_name])
        order_by.append('-pk')
    else:
        order_by = ['-pk', ]
    return order_by


def get_Q_for_collections_page(price_max: Union[str, float], price_min: Union[str, float], filters: dict) -> Q:
    Q_ = _update_Q_by_price(price_max, price_min)

    Q_type = _get_Q_or('type__type__icontains', filters['type'])
    Q_color = _get_Q_or('color__icontains', filters['color'])

    if filters['size']:
        Q_ = Q_ & Q(('type__size__in', _get_condition_by_size(filters['size'])))

    if filters['collection']:
         Q_ = Q_ & Q(('collection__name__in', filters['collection']))

    if Q_type:
        if Q_color:
            return Q_ & Q_type & Q_color
        return Q_ & Q_type
    if Q_color:
        return Q_ & Q_color
    return Q_


class FilteringError(Exception):
    """Exception class when processing filtering data"""


def get_context_by_filter(request) -> dict:
    request_dict = dict(request.POST)
    price_min = get_price('min', request_dict)
    price_max = get_price('max', request_dict)
    max_catalog_price = float(collections.get_max_price_catalog(collections.get_catalog()))
    if price_max < price_min:
        raise FilteringError('The min price can not more max price')

    filters_for_paginated, active_filters = get_filters_for_pagination_and_active_filter(request_dict)
    order_by = get_order_by(filters_for_paginated)

    Q_ = get_Q_for_collections_page(price_max, price_min, filters_for_paginated)
    max_price_more_max_catalog_price_or_equal_to_him = (price_max == max_catalog_price or price_max > max_catalog_price)
    if not Q_ or (not active_filters and (max_price_more_max_catalog_price_or_equal_to_him and price_min < 1)):
        raise FilteringError('''Complex searches cannot be created with these filters. Either there are no active '''
                             '''filters and the max price is equal to the catalog's max price or greater than the '''
                             '''catalog's max price, and the min price is less than 1''')

    filtered_products = products.get_products_filtered_by_Q_ordered_by_specified_list(Q_, order_by)
    if not filtered_products:
        raise FilteringError('There are no data for such filters')

    page = request.POST.get('page')
    return collections.get_context_for_collections_view(active_filters, filters_for_paginated, filtered_products,
                                                        price_max, price_min, page)


def _get_Q_or(filter_, list_value) -> Union[Q, None]:
    if list_value:
        Q_ = Q((filter_, list_value[0]))
        try:
            for filter_value in list_value[1:]:
                Q_ = Q_ | Q((filter_, filter_value))
        except:
            pass
        finally:
            return Q_
    else:
        return None


def _update_Q_by_price(price_max: float, price_min: float) -> Q:
    Q_ = Q(('price__lte', price_max))

    if price_min != '0':
        if Q_:
            Q_ = Q_ & Q(('price__gte', price_min))
        else:
            Q_ = Q(('price__gte', price_min))
    return Q_


def _get_condition_by_size(selected_size: List[str]) ->List[str]:
    size_list = ['S', 'M', 'L', 'XL']
    variables = []
    if len(selected_size) == 1:
        _append_variable(selected_size[0], variables, size_list)
    else:
        for size in selected_size:
            _append_variable(size, variables, size_list)
    return variables


def _append_variable(size: str, variables: list, size_list: List[str]) -> None:
    variables.append(size)
    for size_after_selected in size_list[size_list.index(size)::]:
        for size_before_selected in size_list[:size_list.index(size)+1:]:
            variables.append(size_before_selected+'-'+size_after_selected)
