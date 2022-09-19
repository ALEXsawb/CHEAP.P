from typing import List
from django import template
from django.db.models import QuerySet
from online_store.models import Product

register = template.Library()


@register.simple_tag
def new_variable(variable):
    return variable


@register.simple_tag
def get_catalog_colors(catalog: (list, QuerySet)) -> List[str]:
    return _get_colors_or_sizes_from_catalog(catalog, _append_new_colors_to_catalog_colors)


@register.simple_tag
def get_catalog_sizes(catalog: (list, QuerySet)) -> List[str]:
    return _get_colors_or_sizes_from_catalog(catalog, _append_new_sizes_to_catalog_sizes)


def _get_colors_or_sizes_from_catalog(catalog: (QuerySet, list), append_new_elem_to_list_function) -> List[str]:
    catalog_colors_or_sizes = []
    for collection in catalog:
        for product in collection:
            append_new_elem_to_list_function(product, catalog_colors_or_sizes)
    return catalog_colors_or_sizes


def _append_new_colors_to_catalog_colors(product: Product, catalog_colors: list) -> None:
    for color in product.get_color_list():
        _append_elem_if_elem_not_in_list(color, catalog_colors)


def _append_new_sizes_to_catalog_sizes(product: Product, catalog_sizes: list) -> None:
    for size in product.get_size_list():
        _append_elem_if_elem_not_in_list(size, catalog_sizes)


def _append_elem_if_elem_not_in_list(elem: str, element_list: list) -> None:
    if elem not in element_list:
        element_list.append(elem)
