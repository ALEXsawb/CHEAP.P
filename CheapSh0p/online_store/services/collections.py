from django.core.paginator import Paginator
from django.db.models import QuerySet

from online_store.models import Collection
from .products import get_all_published_products_with_collection_data
from .decorators import max_price_from_cache
from django.core.cache import cache


__all__ = ['splitting_products_by_row', 'get_hot_collection', 'get_all_public_collections', 'get_catalog',
           'CollectionMixin', 'get_collection_max_price', 'get_max_price_catalog', 'get_page']


def splitting_products_by_row(products: list) -> list:
    catalog = []
    products_len = len(products)
    if products_len > 3:
        number_product_in_row = 3
        start_ = 3
        end_ = products_len + number_product_in_row
        for row_limiter in range(start_, end_, 3):
            catalog.append(products[row_limiter - number_product_in_row:row_limiter:])
        return catalog
    catalog.append(products)
    return catalog


def get_hot_collection() -> QuerySet:
    return Collection.objects.order_by('-views')[0]


def get_all_public_collections() -> QuerySet:
    return Collection.objects.filter(is_published=True).order_by('-pk')


def get_catalog() -> list:
    products = get_all_published_products_with_collection_data().select_related('type')
    return splitting_products_by_row(products)


class CollectionMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        context['all_public_collections'] = get_all_public_collections()
        context['css'] = 'catalog.css'
        return context


@max_price_from_cache
def get_max_price_catalog(collections: list) -> str:
    max_price = 0
    for collection in collections:
        max_collection_price = search_max_price_by_collection_products(collection)
        if max_price < max_collection_price:
            max_price = max_collection_price
    cache.set('max_product_price', float(max_price), 86400)
    return str(max_price)


@max_price_from_cache
def get_collection_max_price(collection: list) -> str:
    return str(search_max_price_by_collection_products(collection))


def search_max_price_by_collection_products(collection: list):
    max_collection_price = 0
    for product in collection:
        if product.price > max_collection_price:
            max_collection_price = product.price
    return max_collection_price


def get_page(collection_slug: str, paginate_by: int) -> int:
    return get_all_public_collections().filter(pk__gt=Collection.objects.get(slug=collection_slug).pk
                                               ).count() // paginate_by


def get_context_for_collections_view(active_filters: list, filters_for_paginated: dict, products: QuerySet,
                                     price_max: float, price_min: float, page) -> dict:
    context = {'filters': active_filters, 'filters_for_paginated': filters_for_paginated, }

    if products:
        context['max_product_price'] = str(price_max)
        context['min_product_price'] = str(price_min)

    context['page_obj'] = Paginator(splitting_products_by_row(products), 3).get_page(page)
    context['catalog'] = context['page_obj'].object_list
    return context
