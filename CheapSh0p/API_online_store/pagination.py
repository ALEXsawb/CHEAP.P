from rest_framework.pagination import PageNumberPagination

from API_online_store.utils import get_types_without_products


class BasePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'


class CatalogAPIListPagination(BasePagination):
    pass


class TypeClothingListAPIPagination(BasePagination):
    def paginate_queryset(self, queryset, request, view):
        if 'ForStaff' in view.serializer_class.__name__:
            types_without_products = list(get_types_without_products(view.kwargs['id_types_with_products']))
            return super().paginate_queryset(list(queryset.values())+types_without_products, request, view)
        return super().paginate_queryset(list(queryset.values()), request, view)