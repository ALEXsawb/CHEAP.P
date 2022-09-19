from rest_framework import serializers
from .mixins import CustomSerializerMixin
from .product import ProductSerializerForTypeClothing
from online_store.models import TypeClothing, Product


class TypeClothingForListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='type-detail', lookup_field='slug')
    name = serializers.CharField(source='type', read_only=True)
    color_list = serializers.ListField(source='get_color_list', read_only=True)
    size_list = serializers.ListField(source='get_size_list', read_only=True)

    class Meta:
        model = TypeClothing
        fields = ['name', 'url', 'description', 'characteristics', 'delivery', 'color_list', 'size_list']


class TypeClothingSerializer(TypeClothingForListSerializer):
    products = serializers.SerializerMethodField()

    def get_products(self, obj):
        return ProductSerializerForTypeClothing(Product.objects.filter(type=obj).select_related('collection', 'type'),
                                                many=True, context=self.context).data

    class Meta:
        model = TypeClothing
        fields = ['name', 'description', 'characteristics', 'delivery', 'color_list', 'size_list', 'products']


class TypeClothingListSerializer(CustomSerializerMixin, serializers.Serializer):
    def to_representation(self, instance):
        type_ = TypeClothingForListSerializer(instance[0].type, context=self.context).data
        type_['products'] = ProductSerializerForTypeClothing(instance, many=True, context=self.context).data
        return type_
