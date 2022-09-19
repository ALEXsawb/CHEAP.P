from django.template.defaultfilters import slugify
from rest_framework import serializers

from online_store.models import Collection, TypeClothing, Product
from .mixins import CustomSerializerMixin
from .utils import get_correct_sizes_from_list, update_nested_object_data
from .collection import CollectionSerializerForCatalog, CollectionSerializer
from .product import ProductSerializer, ProductSerializerForCollection, ProductSerializerForTypeClothing
from .type_collection import TypeClothingSerializer

__all__ = ['ProductSerializerForStaff', 'CollectionSerializerForStaff', 'TypeClothingSerializerForStaff',
           'TypeClothingListSerializerForStaff']


class TypeClothingListSerializerForStaff(CustomSerializerMixin, serializers.Serializer):
    def to_representation(self, instance):
        if isinstance(instance, TypeClothing):
            type_without_products = TypeClothingSerializerForStaff(instance, context=self.context).data
            type_without_products['products'] = []
            return type_without_products
        type_ = TypeClothingSerializerForStaff(instance[0].type, context=self.context).data
        type_['products'] = ProductSerializerForTypeClothing(instance, many=True, context=self.context).data
        return type_


class TypeClothingSerializerForStaff(TypeClothingSerializer):
    color_list = serializers.ListField(source='get_color_list')
    size_list = serializers.ListField(source='get_size_list')
    name = serializers.CharField(source='type')

    def update(self, instance, validated_data):
        color_list = validated_data.pop('get_color_list')
        size_list = validated_data.pop('get_size_list')
        if color_list != instance.get_color_list():
            instance.colors = ','.join(color_list)
        if size_list != instance.get_size_list():
            instance.size = get_correct_sizes_from_list(size_list)
        instance.save()
        return super().update(instance, validated_data)

    class Meta:
        model = TypeClothing
        fields = ['id', 'name', 'url', 'description', 'characteristics', 'delivery', 'color_list', 'size_list',
                  'products', 'views']
        depth = 1


class CollectionSerializerForStaff(CollectionSerializer):
    def get_products(self, obj):
        return ProductSerializerForCollection(obj.get_products_this_collection().select_related('type', 'collection',),
                                              many=True, context=self.context).data

    class Meta:
        model = Collection
        read_only_fields = ['products']
        fields = ['id', 'name', 'description', 'is_published', 'slug', 'views', 'products']
        depth = 1


class CollectionSerializerForProductSerializerStaff(CollectionSerializerForCatalog):
    class Meta:
        model = Collection
        fields = ['id', 'name', 'url', 'description']


class TypeClothingSerializerForProductSerializerStaff(serializers.ModelSerializer):
    name = serializers.CharField(source='type')
    url = serializers.HyperlinkedIdentityField(view_name='type-detail', lookup_field='slug')

    class Meta:
        model = TypeClothing
        fields = ['name', 'url', 'description', 'characteristics', 'delivery']


class ProductSerializerForStaff(ProductSerializer):
    collection = CollectionSerializerForProductSerializerStaff()
    type = TypeClothingSerializerForProductSerializerStaff()

    class Meta:
        model = Product
        read_only_fields = ['type', 'time_create', 'time_update']
        fields = ['id', 'name', 'slug', 'url', 'collection', 'price', 'photo', 'is_published', 'description_print',
                  'size_list', 'color_list', 'type', 'time_create', 'time_update', 'views']
        depth = 1

    def update(self, instance, validated_data):
        collection_update_data = validated_data.pop('collection', None)
        type_update_data = validated_data.pop('type', None)

        if instance.collection.slug != slugify(collection_update_data['name']):
            update_nested_object_data(instance, 'collection', Collection, slugify(collection_update_data['name']))
        if instance.type.slug != slugify(type_update_data['type']):
            update_nested_object_data(instance, 'type', TypeClothing, slugify(type_update_data['type']))
        return super().update(instance, validated_data)
