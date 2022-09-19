from rest_framework import serializers

from .mixins import CustomSerializerMixin
from online_store.models import Collection
from .product import ProductSerializerForCollection


class CatalogSerializer(CustomSerializerMixin, serializers.Serializer):
    def to_representation(self, instance):
        collection = CollectionSerializerForCatalog(instance[0].collection, context=self.context).data
        collection['products'] = ProductSerializerForCollection(instance, many=True, context=self.context).data
        return collection


class CollectionSerializerForCatalog(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='collection-detail', lookup_field='slug')

    class Meta:
        model = Collection
        fields = ['name', 'url', 'description']


class CollectionSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    def get_products(self, obj):
        return ProductSerializerForCollection(obj.get_products_this_collection().select_related('type', 'collection',),
                                              many=True, context=self.context).data

    class Meta:
        model = Collection
        fields = ['name', 'description', 'products']
