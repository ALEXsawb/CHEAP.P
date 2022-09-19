from django.db.models import QuerySet, Q
from online_store.models import Product, TypeClothing, Collection


def get_types_products(products: QuerySet) -> dict:
    types_products = {}
    products_type = []
    for product in products:
        type_id = product.type.pk
        if not types_products:
            types_products[type_id] = [product, ]
            products_type.append(product)
        elif product.type.pk in types_products.keys():
            products_type.append(product)
        else:
            products_type = []
            types_products[type_id] = [product, ]
            products_type.append(product)
        types_products[type_id] = products_type
    return types_products


def get_products_for_type_clothing_list():
    return Product.objects.order_by('-type__pk', ).select_related('type', 'collection')


def get_products_for_catalog():
    return Product.objects.select_related('collection', 'type').order_by('-collection__pk')


def get_types_without_products(id_types_with_products):
    return TypeClothing.objects.filter(~Q(pk__in=id_types_with_products))


def get_is_published_collections_with_views_data_ordered():
    return Collection.objects.filter(is_published=True).order_by('-pk')


def get_products_with_collection_and_type_data():
    return Product.objects.all().select_related('collection', 'type')


def get_all_types_clothing():
    return TypeClothing.objects.all()
