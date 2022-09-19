from rest_framework.reverse import reverse
from rest_framework import serializers

from .utils import get_name_and_url_object
from online_store.models import Product


class ProductHyperLink(serializers.HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, forms):
        return reverse(view_name, kwargs={'collection_slug': obj.collection.slug, 'slug': obj.slug}, request=request)


class ProductSerializerForOtherSerializers(serializers.ModelSerializer):
    url = ProductHyperLink(view_name='product-detail', lookup_url_kwarg=('collection_slug', 'slug'))
    collection = serializers.SerializerMethodField()
    size_list = serializers.ListField(source='get_size_list', read_only=True)
    color_list = serializers.ListField(source='get_color_list', read_only=True)

    def get_collection(self, obj):
        return get_name_and_url_object(self, obj, 'collection')


class ProductSerializerForTypeClothing(ProductSerializerForOtherSerializers, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'photo', 'url', 'collection', 'price', 'color_list', 'size_list']
        depth = 1


class ProductSerializer(ProductSerializerForOtherSerializers, serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        type_dict = get_name_and_url_object(self, obj, 'type')
        type_dict['description'] = obj.type.description
        type_dict['characteristics'] = obj.type.characteristics
        type_dict['delivery'] = obj.type.delivery
        return type_dict

    class Meta:
        model = Product
        fields = ['name', 'photo', 'collection', 'type', 'price', 'color_list', 'size_list']
        depth = 1


class ProductSerializerForCollection(ProductSerializerForOtherSerializers):
    type = serializers.CharField(source='type.type', read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'photo', 'url', 'type', 'price', 'color_list', 'size_list']
