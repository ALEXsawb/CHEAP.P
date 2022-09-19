from typing import Union

from django.db.models import F, QuerySet, Model
from online_store.models import Collection, TypeClothing, Product


def _add_view(obj: Union[QuerySet, Model]) -> None:
    if not isinstance(obj, QuerySet):
        obj = obj.__class__.objects.filter(pk=obj.id)
    obj.update(views=F('views') + 1)


def set_views_for_collection(collection: Collection) -> None:
    _add_view(collection)


def set_views_for_type(type_: TypeClothing) -> None:
    _add_view(type_)


def set_views_for_product(product: Union[QuerySet, Product]) -> None:
    _add_view(product)
    if not isinstance(product, QuerySet):
        set_views_for_type(product.type)
    else:
        set_views_for_type(product[0].type)
