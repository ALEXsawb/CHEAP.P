from rest_framework import generics, mixins
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.viewsets import GenericViewSet
from rest_framework.authtoken import views

from .pagination import CatalogAPIListPagination, TypeClothingListAPIPagination
from online_store.services.collections import splitting_products_by_row
from .serializers import *
from .utils import *
from .permission import AdminOrRead


class CatalogAPI(generics.ListAPIView):
    serializer_class = CatalogSerializer
    pagination_class = CatalogAPIListPagination
    permission_classes = (AdminOrRead,)
    authentication_classes = (SessionAuthentication, BasicAuthentication)

    def get_queryset(self):
        products = get_products_for_catalog()
        products_by_collections = splitting_products_by_row(products)
        return products_by_collections


class TypeClothingAPI(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = get_all_types_clothing()
    serializer_class = TypeClothingSerializer
    permission_classes = (AdminOrRead, )
    lookup_field = 'slug'


class TypeClothingListAPI(generics.ListAPIView):
    permission_classes = (AdminOrRead,)
    serializer_class = TypeClothingListSerializer
    pagination_class = TypeClothingListAPIPagination

    def get_queryset(self):
        products = get_products_for_type_clothing_list()
        queryset = get_types_products(products)
        self.kwargs.update({'id_types_with_products': list(queryset.keys())})
        return queryset


class CollectionAPI(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = get_is_published_collections_with_views_data_ordered()
    serializer_class = CollectionSerializer
    permission_classes = (AdminOrRead,)
    lookup_field = 'slug'


class ProductAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_products_with_collection_and_type_data()
    serializer_class = ProductSerializer
    permission_classes = (AdminOrRead,)
    lookup_field = {'collection_slug', 'slug'}

    def get_object(self):
        filter_ = {'collection__slug': self.kwargs['collection_slug'], 'slug': self.kwargs['slug']}
        return generics.get_object_or_404(self.get_queryset(), **filter_)
