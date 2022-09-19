from online_store.models import Product
from django.db.models import Q, QuerySet


__all__ = ['get_top_clothing', 'get_product_by_slug_with_collection_and_type_data', ]


def get_all_published_products_with_collection_data() -> QuerySet:
    return Product.objects.select_related('collection').filter(is_published=True).order_by('-collection__pk')


def get_top_clothing() -> QuerySet:
    return Product.objects.select_related('collection').filter(is_published=True).order_by('-views')[:4]


def get_product_by_slug_with_collection_and_type_data(slug: str) -> QuerySet:
    return Product.objects.filter(slug=slug).select_related('type', 'collection')


def get_products_filtered_by_Q_ordered_by_specified_list(Q_: Q, order_by: list) -> QuerySet:
    """with collection data"""
    return Product.objects.filter(Q_).order_by(*order_by).select_related('collection')
