from datetime import datetime
from random import choice

from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import serializers

from API_online_store.serializers.collection import CollectionSerializerForCatalog, CollectionSerializer, \
    CatalogSerializer
from API_online_store.serializers.for_staff import TypeClothingSerializerForStaff, TypeClothingListSerializerForStaff, \
    CollectionSerializerForStaff, CollectionSerializerForProductSerializerStaff, \
    TypeClothingSerializerForProductSerializerStaff, ProductSerializerForStaff
from API_online_store.serializers.product import *
from API_online_store.serializers.type_collection import TypeClothingForListSerializer, TypeClothingSerializer, \
    TypeClothingListSerializer
from online_store.models import *


class ProductMixin:
    @classmethod
    def setUpTestData(cls):
        OrderForm.objects.create(full_name='ALex', first_address='first address',
                                 second_address='second address', country='UA',
                                 postal_or_zip_code='50050', city='KR', phone='phone',
                                 email='lapus@ssds.com',
                                 company='fdfsfsdf')
        cls.collection = Collection.objects.create(name='test collection', description='test_collection_description',
                                                   views=0)
        cls.type_ = TypeClothing.objects.create(type='test_type', description='test_type_description',
                                                characteristics='test_characteristics', colors='black, white',
                                                delivery='7 - 14 day', size='S, M, XL', slug='test-type-slug',
                                                views=0)
        cls.product = Product.objects.create(collection=cls.collection, name='product 1',
                                             type=cls.type_, price='55.33', color='white',
                                             description_print='description_print_test',
                                             views=100)
        cls.request = APIRequestFactory().get(reverse('product-detail',
                                                      kwargs={'collection_slug': cls.product.collection.slug,
                                                              'slug': cls.product.slug}))


class ProductSerializerForOtherSerializersTest(TestCase):
    def test_declared_fields(self):
        declared_fields = ProductSerializerForOtherSerializers._declared_fields
        self.assertIsInstance(declared_fields['url'], ProductHyperLink)
        self.assertIsInstance(declared_fields['collection'], serializers.SerializerMethodField)
        self.assertTrue(ProductSerializerForOtherSerializers.get_collection)
        self.assertIsInstance(declared_fields['size_list'], serializers.ListField)
        self.assertIsInstance(declared_fields['color_list'], serializers.ListField)


class ProductSerializerForTypeClothingTest(ProductMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product2 = Product.objects.create(collection=cls.collection, name='product 2',
                                              type=cls.type_, price='5.33', color='white',
                                              description_print='description_print_test',
                                              views=100)
        cls.product3 = Product.objects.create(collection=cls.collection, name='product 3',
                                              type=cls.type_, price='33.33', color='white',
                                              description_print='description_print_test',
                                              views=100)

    def test_field_presence(self):
        product_data = ProductSerializerForTypeClothing(self.product, context={'request': self.request}).data
        self.assertCountEqual(list(product_data.keys()), ['name', 'photo', 'url', 'collection', 'price', 'color_list',
                                                          'size_list'])
        self.assertCountEqual(list(product_data['collection'].keys()), ['name', 'url'])

    def test_data(self):
        data = {'name': self.product.name,
                'photo': f'http://testserver{self.product.photo.url}',
                'url': 'http://testserver/api/v1/catalog/test-collection/product-1',
                'collection': {'name': self.collection.name,
                               'url': 'http://testserver/api/v1/catalog/test-collection'},
                'price': self.product.price,
                'color_list': self.product.get_color_list(),
                'size_list': self.product.get_size_list()
                }
        self.assertEqual(ProductSerializerForTypeClothing(self.product, context={'request': self.request}).data, data)

    def test_many_data(self):
        data = [{'name': self.product.name,
                 'photo': f'http://testserver{self.product.photo.url}',
                 'url': 'http://testserver/api/v1/catalog/test-collection/product-1',
                 'collection': {'name': self.collection.name,
                                'url': 'http://testserver/api/v1/catalog/test-collection'},
                 'price': self.product.price,
                 'color_list': self.product.get_color_list(),
                 'size_list': self.product.get_size_list()
                 },
                {'name': self.product2.name,
                 'photo': f'http://testserver{self.product2.photo.url}',
                 'url': 'http://testserver/api/v1/catalog/test-collection/product-2',
                 'collection': {'name': self.collection.name,
                                'url': 'http://testserver/api/v1/catalog/test-collection'},
                 'price': self.product2.price,
                 'color_list': self.product2.get_color_list(),
                 'size_list': self.product2.get_size_list()
                 },
                {'name': self.product3.name,
                 'photo': f'http://testserver{self.product3.photo.url}',
                 'url': 'http://testserver/api/v1/catalog/test-collection/product-3',
                 'collection': {'name': self.collection.name,
                                'url': 'http://testserver/api/v1/catalog/test-collection'},
                 'price': self.product3.price,
                 'color_list': self.product3.get_color_list(),
                 'size_list': self.product3.get_size_list()
                 }
                ]
        self.assertEqual(ProductSerializerForTypeClothing([self.product, self.product2, self.product3], many=True,
                                                          context={'request': self.request}).data, data)


class ProductSerializerTest(ProductMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product2 = Product.objects.create(collection=cls.collection, name='product 2',
                                              type=cls.type_, price='5.33', color='white',
                                              description_print='description_print_test',
                                              views=100)
        cls.product3 = Product.objects.create(collection=cls.collection, name='product 3',
                                              type=cls.type_, price='33.33', color='white',
                                              description_print='description_print_test',
                                              views=100)

    def test_field_presence(self):
        product_data = ProductSerializer(self.product, context={'request': self.request}).data
        self.assertCountEqual(list(product_data.keys()), ['name', 'photo', 'collection', 'type', 'price', 'color_list',
                                                          'size_list'])
        self.assertCountEqual(list(product_data['collection'].keys()), ['name', 'url'])
        self.assertCountEqual(list(product_data['type'].keys()), ['name', 'url', 'description', 'characteristics',
                                                                  'delivery'])

    def test_data(self):
        data = {'name': self.product.name,
                'photo': f'http://testserver{self.product.photo.url}',
                'collection': {'name': self.collection.name,
                               'url': 'http://testserver/api/v1/catalog/test-collection'},
                'type': {'name': self.product.type.type,
                         'url': 'http://testserver/api/v1/type/test_type',
                         'description': self.product.type.description,
                         'characteristics': self.product.type.characteristics,
                         'delivery': self.product.type.delivery
                         },
                'price': self.product.price,
                'color_list': self.product.get_color_list(),
                'size_list': self.product.get_size_list()
                }
        self.assertEqual(ProductSerializer(self.product, context={'request': self.request}).data, data)

    def test_many_data(self):
        data = [{'name': self.product.name,
                 'photo': f'http://testserver{self.product.photo.url}',
                 'collection': {'name': self.collection.name,
                                'url': 'http://testserver/api/v1/catalog/test-collection'},
                 'type': {'name': self.product.type.type,
                          'url': 'http://testserver/api/v1/type/test_type',
                          'description': self.product.type.description,
                          'characteristics': self.product.type.characteristics,
                          'delivery': self.product.type.delivery
                          },
                 'price': self.product.price,
                 'color_list': self.product.get_color_list(),
                 'size_list': self.product.get_size_list()
                 },
                {'name': self.product2.name,
                 'photo': f'http://testserver{self.product2.photo.url}',
                 'collection': {'name': self.product2.collection.name,
                                'url': 'http://testserver/api/v1/catalog/test-collection'},
                 'type': {'name': self.product2.type.type,
                          'url': 'http://testserver/api/v1/type/test_type',
                          'description': self.product2.type.description,
                          'characteristics': self.product2.type.characteristics,
                          'delivery': self.product2.type.delivery
                          },
                 'price': self.product2.price,
                 'color_list': self.product2.get_color_list(),
                 'size_list': self.product2.get_size_list()
                 },
                {'name': self.product3.name,
                 'photo': f'http://testserver{self.product3.photo.url}',
                 'collection': {'name': self.product3.collection.name,
                                'url': 'http://testserver/api/v1/catalog/test-collection'},
                 'type': {'name': self.product3.type.type,
                          'url': 'http://testserver/api/v1/type/test_type',
                          'description': self.product3.type.description,
                          'characteristics': self.product3.type.characteristics,
                          'delivery': self.product3.type.delivery
                          },
                 'price': self.product3.price,
                 'color_list': self.product3.get_color_list(),
                 'size_list': self.product3.get_size_list()
                 }
                ]
        self.assertEqual(ProductSerializer([self.product, self.product2, self.product3], many=True,
                                           context={'request': self.request}).data, data)


class ProductSerializerForCollectionTest(ProductMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product2 = Product.objects.create(collection=cls.collection, name='product 2',
                                              type=cls.type_, price='5.33', color='white',
                                              description_print='description_print_test',
                                              views=100)
        cls.product3 = Product.objects.create(collection=cls.collection, name='product 3',
                                              type=cls.type_, price='33.33', color='white',
                                              description_print='description_print_test',
                                              views=100)

    def test_field_presence(self):
        product_data = ProductSerializerForCollection(self.product, context={'request': self.request}).data
        self.assertCountEqual(list(product_data.keys()), ['name', 'photo', 'url', 'type', 'price', 'color_list',
                                                          'size_list'])

    def test_data(self):
        data = {'name': self.product.name,
                'photo': f'http://testserver{self.product.photo.url}',
                'url': 'http://testserver/api/v1/catalog/test-collection/product-1',
                'type': self.product.type.type,
                'price': self.product.price,
                'color_list': self.product.get_color_list(),
                'size_list': self.product.get_size_list()
                }
        self.assertEqual(ProductSerializerForCollection(self.product, context={'request': self.request}).data, data)

    def test_many_data(self):
        data = [{'name': self.product.name,
                 'photo': f'http://testserver{self.product.photo.url}',
                 'url': 'http://testserver/api/v1/catalog/test-collection/product-1',
                 'type': self.product.type.type,
                 'price': self.product.price,
                 'color_list': self.product.get_color_list(),
                 'size_list': self.product.get_size_list()
                 },
                {'name': self.product2.name,
                 'photo': f'http://testserver{self.product2.photo.url}',
                 'url': 'http://testserver/api/v1/catalog/test-collection/product-2',
                 'type': self.product2.type.type,
                 'price': self.product2.price,
                 'color_list': self.product2.get_color_list(),
                 'size_list': self.product2.get_size_list()
                 },
                {'name': self.product3.name,
                 'photo': f'http://testserver{self.product3.photo.url}',
                 'url': 'http://testserver/api/v1/catalog/test-collection/product-3',
                 'type': self.product3.type.type,
                 'price': self.product3.price,
                 'color_list': self.product3.get_color_list(),
                 'size_list': self.product3.get_size_list()
                 }
                ]
        self.assertEqual(ProductSerializerForCollection([self.product, self.product2, self.product3], many=True,
                                                        context={'request': self.request}).data, data)


class CollectionSerializerForCatalogTest(ProductMixin, TestCase):
    def test_field_presence(self):
        collection_data = CollectionSerializerForCatalog(self.collection,
                                                         context={'request': self.request}).data
        self.assertCountEqual(list(collection_data.keys()), ['name', 'url', 'description'])

    def test_data(self):
        data = {'name': self.collection.name,
                'url': 'http://testserver/api/v1/catalog/test-collection',
                'description': self.collection.description
                }
        self.assertEqual(CollectionSerializerForCatalog(self.collection, context={'request': self.request}).data, data)


class CollectionSerializerTest(TestCase):
    fixtures = ['test_db.json']

    @classmethod
    def setUpTestData(cls):
        cls.collection_1 = choice(Collection.objects.all())
        cls.collection_2 = choice(Collection.objects.all())
        cls.collection_3 = choice(Collection.objects.all())
        cls.request = APIRequestFactory().get(reverse('collection-detail', kwargs={'slug': cls.collection_1.slug}))

    def test_field_presence(self):
        collection_data = CollectionSerializer(self.collection_1, context={'request': self.request}).data
        self.assertCountEqual(list(collection_data.keys()), ['name', 'description', 'products'])
        self.assertCountEqual(list(collection_data['products'][0].keys()), ['name', 'photo', 'url', 'type', 'price',
                                                                            'color_list', 'size_list'])

    def test_data(self):
        data = {'name': self.collection_1.name,
                'description': self.collection_1.description,
                'products': ProductSerializerForCollection(self.collection_1.product_set, many=True,
                                                           context={'request': self.request}).data
                }
        self.assertEqual(CollectionSerializer(self.collection_1, context={'request': self.request}).data, data)

    def test_many_data(self):
        data = [{'name': self.collection_1.name,
                 'description': self.collection_1.description,
                 'products': ProductSerializerForCollection(self.collection_1.product_set, many=True,
                                                            context={'request': self.request}).data

                 },
                {'name': self.collection_2.name,
                 'description': self.collection_2.description,
                 'products': ProductSerializerForCollection(self.collection_2.product_set, many=True,
                                                            context={'request': self.request}).data
                 },
                {'name': self.collection_3.name,
                 'description': self.collection_3.description,
                 'products': ProductSerializerForCollection(self.collection_3.product_set, many=True,
                                                            context={'request': self.request}).data
                 },
                ]
        self.assertEqual(CollectionSerializer([self.collection_1, self.collection_2, self.collection_3],
                                              context={'request': self.request}, many=True).data, data)


class CatalogSerializerTest(TestCase):
    fixtures = ['test_db.json']

    @classmethod
    def setUpTestData(cls):
        cls.collection_1 = choice(Collection.objects.all())
        cls.collection_2 = choice(Collection.objects.all())
        cls.collection_3 = choice(Collection.objects.all())
        cls.request = APIRequestFactory().get(reverse('collection-detail', kwargs={'slug': cls.collection_1.slug}))

    def test_field_presence(self):
        collection_data = CatalogSerializer(self.collection_1.product_set.all(),
                                            context={'request': self.request}).data
        self.assertCountEqual(list(collection_data.keys()), ['name', 'url', 'description', 'products'])
        self.assertCountEqual(list(collection_data['products'][0].keys()), ['name', 'photo', 'url', 'type', 'price',
                                                                            'color_list', 'size_list'])

    def test_data(self):
        data = {'name': self.collection_1.name,
                'url': f'http://testserver/api/v1{self.collection_1.get_absolute_url()}',
                'description': self.collection_1.description,
                'products': ProductSerializerForCollection(self.collection_1.product_set, many=True,
                                                           context={'request': self.request}).data
                }
        self.assertEqual(CatalogSerializer(self.collection_1.product_set.all(),
                                           context={'request': self.request}).data, data)

    def test_many_data(self):
        data = [{'name': self.collection_1.name,
                 'url': f'http://testserver/api/v1{self.collection_1.get_absolute_url()}',
                 'description': self.collection_1.description,
                 'products': ProductSerializerForCollection(self.collection_1.product_set, many=True,
                                                            context={'request': self.request}).data
                 },
                {'name': self.collection_2.name,
                 'url': f'http://testserver/api/v1{self.collection_2.get_absolute_url()}',
                 'description': self.collection_2.description,
                 'products': ProductSerializerForCollection(self.collection_2.product_set, many=True,
                                                            context={'request': self.request}).data
                 },
                {'name': self.collection_3.name,
                 'url': f'http://testserver/api/v1{self.collection_3.get_absolute_url()}',
                 'description': self.collection_3.description,
                 'products': ProductSerializerForCollection(self.collection_3.product_set, many=True,
                                                            context={'request': self.request}).data
                 },
                ]
        self.assertEqual(CatalogSerializer([self.collection_1.product_set.all(), self.collection_2.product_set.all(),
                                            self.collection_3.product_set.all()], many=True,
                                           context={'request': self.request}).data, data)


class TypeClothingForListSerializerTest(TestCase):
    fixtures = ['test_db.json']

    @classmethod
    def setUpTestData(cls):
        cls.type_1 = choice(TypeClothing.objects.all())
        cls.type_2 = choice(TypeClothing.objects.all())
        cls.type_3 = choice(TypeClothing.objects.all())
        cls.request = APIRequestFactory().get(reverse('type-detail', kwargs={'slug': cls.type_1.slug}))

    def test_field_presence(self):
        type_data = TypeClothingForListSerializer(self.type_1, context={'request': self.request}).data
        self.assertCountEqual(list(type_data.keys()), ['name', 'url', 'description', 'characteristics', 'delivery',
                                                       'color_list', 'size_list'])

    def test_data(self):
        data = {
            'name': self.type_1.type,
            'url': f'http://testserver/api/v1/type/{self.type_1.slug}',
            'description': self.type_1.description,
            'characteristics': self.type_1.characteristics,
            'delivery': self.type_1.delivery,
            'color_list': self.type_1.get_color_list(),
            'size_list': self.type_1.get_size_list()
        }
        self.assertEqual(TypeClothingForListSerializer(self.type_1, context={'request': self.request}).data, data)

    def test_many_data(self):
        data = [{'name': self.type_1.type,
                 'url': f'http://testserver/api/v1/type/{self.type_1.slug}',
                 'description': self.type_1.description,
                 'characteristics': self.type_1.characteristics,
                 'delivery': self.type_1.delivery,
                 'color_list': self.type_1.get_color_list(),
                 'size_list': self.type_1.get_size_list()
                 },
                {'name': self.type_2.type,
                 'url': f'http://testserver/api/v1/type/{self.type_2.slug}',
                 'description': self.type_2.description,
                 'characteristics': self.type_2.characteristics,
                 'delivery': self.type_2.delivery,
                 'color_list': self.type_2.get_color_list(),
                 'size_list': self.type_2.get_size_list()
                 },
                {'name': self.type_3.type,
                 'url': f'http://testserver/api/v1/type/{self.type_3.slug}',
                 'description': self.type_3.description,
                 'characteristics': self.type_3.characteristics,
                 'delivery': self.type_3.delivery,
                 'color_list': self.type_3.get_color_list(),
                 'size_list': self.type_3.get_size_list()
                 },
                ]
        self.assertEqual(TypeClothingForListSerializer([self.type_1, self.type_2, self.type_3],
                                                       context={'request': self.request}, many=True).data, data)


class TypeClothingSerializerTest(TestCase):
    fixtures = ['test_db.json']

    @classmethod
    def setUpTestData(cls):
        cls.type_1 = choice(Product.objects.filter(is_published=True)).type
        cls.type_2 = choice(Product.objects.filter(is_published=True)).type
        cls.type_3 = choice(Product.objects.filter(is_published=True)).type
        cls.request = APIRequestFactory().get(reverse('type-detail', kwargs={'slug': cls.type_1.slug}))

    def test_field_presence(self):
        type_data = TypeClothingSerializer(self.type_1, context={'request': self.request}).data
        self.assertCountEqual(list(type_data.keys()), ['name', 'description', 'characteristics', 'delivery',
                                                       'color_list', 'size_list', 'products'])
        self.assertCountEqual(list(type_data['products'][0].keys()), ['name', 'photo', 'url', 'collection', 'price',
                                                                      'color_list', 'size_list'])

    def test_data(self):
        data = {'name': self.type_1.type,
                'description': self.type_1.description,
                'characteristics': self.type_1.characteristics,
                'delivery': self.type_1.delivery,
                'color_list': self.type_1.get_color_list(),
                'size_list': self.type_1.get_size_list(),
                'products': ProductSerializerForTypeClothing(self.type_1.product_set.all(), many=True,
                                                             context={'request': self.request}).data

        }

        self.assertEqual(TypeClothingSerializer(self.type_1, context={'request': self.request}).data, data)

    def test_many_data(self):
        data = [{'name': self.type_1.type,
                 'description': self.type_1.description,
                 'characteristics': self.type_1.characteristics,
                 'delivery': self.type_1.delivery,
                 'color_list': self.type_1.get_color_list(),
                 'size_list': self.type_1.get_size_list(),
                 'products': ProductSerializerForTypeClothing(self.type_1.product_set.all(), many=True,
                                                              context={'request': self.request}).data
                 },
                {'name': self.type_2.type,
                 'description': self.type_2.description,
                 'characteristics': self.type_2.characteristics,
                 'delivery': self.type_2.delivery,
                 'color_list': self.type_2.get_color_list(),
                 'size_list': self.type_2.get_size_list(),
                 'products': ProductSerializerForTypeClothing(self.type_2.product_set.all(), many=True,
                                                              context={'request': self.request}).data
                 },
                {'name': self.type_3.type,
                 'description': self.type_3.description,
                 'characteristics': self.type_3.characteristics,
                 'delivery': self.type_3.delivery,
                 'color_list': self.type_3.get_color_list(),
                 'size_list': self.type_3.get_size_list(),
                 'products': ProductSerializerForTypeClothing(self.type_3.product_set.all(), many=True,
                                                              context={'request': self.request}).data
                 },
                ]
        self.assertCountEqual(TypeClothingSerializer([self.type_1, self.type_2, self.type_3],
                                                     context={'request': self.request}, many=True).data, data)


class TypeClothingListSerializerTest(TestCase):
    fixtures = ['test_db.json']

    @classmethod
    def setUpTestData(cls):
        cls.type_1 = choice(Product.objects.filter(is_published=True)).type
        cls.type_2 = choice(Product.objects.filter(is_published=True)).type
        cls.type_3 = choice(Product.objects.filter(is_published=True)).type
        cls.request = APIRequestFactory().get(reverse('type-detail', kwargs={'slug': cls.type_1.slug}))

    def test_field_presence(self):
        type_data = TypeClothingListSerializer(self.type_1.product_set.all(), context={'request': self.request}).data
        self.assertCountEqual(list(type_data.keys()), ['name', 'url', 'description', 'characteristics', 'delivery',
                                                       'color_list', 'size_list', 'products'])
        self.assertCountEqual(list(type_data['products'][0].keys()), ['name', 'photo', 'url', 'collection', 'price',
                                                                      'color_list', 'size_list'])

    def test_data(self):
        data = {
            'name': self.type_1.type,
            'url': f'http://testserver/api/v1/type/{self.type_1.slug}',
            'description': self.type_1.description,
            'characteristics': self.type_1.characteristics,
            'delivery': self.type_1.delivery,
            'color_list': self.type_1.get_color_list(),
            'size_list': self.type_1.get_size_list(),
            'products': ProductSerializerForTypeClothing(self.type_1.product_set.all(), many=True,
                                                         context={'request': self.request}).data
        }
        self.assertEqual(TypeClothingListSerializer(self.type_1.product_set.all(),
                                                    context={'request': self.request}).data, data)

    def test_many_data(self):
        data = [{'name': self.type_1.type,
                 'url': f'http://testserver/api/v1/type/{self.type_1.slug}',
                 'description': self.type_1.description,
                 'characteristics': self.type_1.characteristics,
                 'delivery': self.type_1.delivery,
                 'color_list': self.type_1.get_color_list(),
                 'size_list': self.type_1.get_size_list(),
                 'products': ProductSerializerForTypeClothing(self.type_1.product_set.all(), many=True,
                                                         context={'request': self.request}).data
                 },
                {'name': self.type_2.type,
                 'url': f'http://testserver/api/v1/type/{self.type_2.slug}',
                 'description': self.type_2.description,
                 'characteristics': self.type_2.characteristics,
                 'delivery': self.type_2.delivery,
                 'color_list': self.type_2.get_color_list(),
                 'size_list': self.type_2.get_size_list(),
                 'products': ProductSerializerForTypeClothing(self.type_2.product_set.all(), many=True,
                                                              context={'request': self.request}).data
                 },
                {'name': self.type_3.type,
                 'url': f'http://testserver/api/v1/type/{self.type_3.slug}',
                 'description': self.type_3.description,
                 'characteristics': self.type_3.characteristics,
                 'delivery': self.type_3.delivery,
                 'color_list': self.type_3.get_color_list(),
                 'size_list': self.type_3.get_size_list(),
                 'products': ProductSerializerForTypeClothing(self.type_3.product_set.all(), many=True,
                                                              context={'request': self.request}).data
                 },
                ]
        self.assertEqual(TypeClothingListSerializer([self.type_1.product_set.all(), self.type_2.product_set.all(),
                                                     self.type_3.product_set.all()], many=True,
                                                    context={'request': self.request}).data, data)


class TypeClothingSerializerForStaffTest(TestCase):
    fixtures = ['test_db.json']

    @classmethod
    def setUpTestData(cls):
        cls.type_1 = choice(TypeClothing.objects.all())
        cls.type_2 = choice(TypeClothing.objects.all())
        cls.type_3 = choice(TypeClothing.objects.all())
        cls.request = APIRequestFactory().get(reverse('type-detail', kwargs={'slug': cls.type_1.slug}))

    def test_field_presence(self):
        type_data = TypeClothingSerializerForStaff(
                                            choice(Product.objects.filter(is_published=True)).type,
                                            context={'request': self.request}).data
        self.assertCountEqual(list(type_data.keys()), ['id', 'url', 'views', 'name', 'description', 'products',
                                                       'characteristics', 'delivery', 'color_list', 'size_list'])
        self.assertCountEqual(list(type_data['products'][0].keys()), ['name', 'photo', 'url', 'collection', 'price',
                                                                      'color_list', 'size_list'])

    def test_data(self):
        data = {'id': self.type_1.pk,
                'views': self.type_1.views,
                'url': f'http://testserver/api/v1/type/{self.type_1.slug}',
                'name': self.type_1.type,
                'description': self.type_1.description,
                'characteristics': self.type_1.characteristics,
                'delivery': self.type_1.delivery,
                'color_list': self.type_1.get_color_list(),
                'size_list': self.type_1.get_size_list(),
                }
        if self.type_1.product_set.all():
            data['products'] = ProductSerializerForTypeClothing(self.type_1.product_set.all(), many=True,
                                                                context={'request': self.request}).data
        else:
            data['products'] = []
        self.assertEqual(TypeClothingSerializerForStaff(self.type_1, context={'request': self.request}).data, data)

    def test_many_data(self):
        data = [{'id': self.type_1.pk,
                'views': self.type_1.views,
                 'url': f'http://testserver/api/v1/type/{self.type_1.slug}',
                 'name': self.type_1.type,
                 'description': self.type_1.description,
                 'characteristics': self.type_1.characteristics,
                 'delivery': self.type_1.delivery,
                 'color_list': self.type_1.get_color_list(),
                 'size_list': self.type_1.get_size_list(),
                 },
                {'id': self.type_2.pk,
                 'views': self.type_2.views,
                 'url': f'http://testserver/api/v1/type/{self.type_2.slug}',
                 'name': self.type_2.type,
                 'description': self.type_2.description,
                 'characteristics': self.type_2.characteristics,
                 'delivery': self.type_2.delivery,
                 'color_list': self.type_2.get_color_list(),
                 'size_list': self.type_2.get_size_list(),
                 },
                {'id': self.type_3.pk,
                 'views': self.type_3.views,
                 'url': f'http://testserver/api/v1/type/{self.type_3.slug}',
                 'name': self.type_3.type,
                 'description': self.type_3.description,
                 'characteristics': self.type_3.characteristics,
                 'delivery': self.type_3.delivery,
                 'color_list': self.type_3.get_color_list(),
                 'size_list': self.type_3.get_size_list(),
                 },
                ]
        types = [self.type_1, self.type_2, self.type_3]
        for type_clothing_id in range(3):
            if types[type_clothing_id].product_set.all():
                data[type_clothing_id]['products'] = ProductSerializerForTypeClothing(list(
                                                               types[type_clothing_id].product_set.all()), many=True,
                                                               context={'request': self.request}).data
            else:
                data[type_clothing_id]['products'] = list()
        self.assertEqual(TypeClothingSerializerForStaff([self.type_1, self.type_2, self.type_3],
                                                        context={'request': self.request}, many=True).data, data)

    def test_update_colors(self):
        type_1 = TypeClothing.objects.get(pk=choice(Product.objects.filter(is_published=True)).type.pk)
        serialized_data = TypeClothingSerializerForStaff(type_1, context={'request': self.request})
        validated_data = serialized_data.data
        all_products_with_type = Product.objects.filter(type=type_1.pk)
        validated_data['get_color_list'] = ['black', ]
        validated_data['get_size_list'] = type_1.get_size_list()
        validated_data['views'] = type_1.views

        serialized_data.update(instance=type_1, validated_data=validated_data)
        for product in all_products_with_type:
            if product.is_published:
                self.assertIn(product.color, type_1.colors)

    def test_update_sizes(self):
        type_1 = TypeClothing.objects.get(pk=choice(Product.objects.filter(is_published=True)).type.pk)
        serialized_data = TypeClothingSerializerForStaff(type_1, context={'request': self.request})
        validated_data = serialized_data.data
        validated_data['get_color_list'] = type_1.get_color_list()
        validated_data['get_size_list'] = ['S', 'L', 'XL']
        validated_data['views'] = type_1.views

        serialized_data.update(instance=type_1, validated_data=validated_data)
        type_1.refresh_from_db()
        self.assertEqual(type_1.get_size_list(), ['S', 'L', 'XL'])

    def test_update_name(self):
        type_1 = TypeClothing.objects.get(pk=choice(Product.objects.filter(is_published=True)).type.pk)
        serialized_data = TypeClothingSerializerForStaff(type_1, context={'request': self.request})
        validated_data = serialized_data.data
        validated_data['get_color_list'] = type_1.get_color_list()
        validated_data['get_size_list'] = type_1.get_size_list()
        validated_data['views'] = type_1.views
        validated_data['name'] = type_1.name = 'Bavovna'

        serialized_data.update(instance=type_1, validated_data=validated_data)
        type_1.refresh_from_db()
        self.assertEqual(type_1.name, 'Bavovna')

    def test_update_description(self):
        type_1 = TypeClothing.objects.get(pk=choice(Product.objects.filter(is_published=True)).type.pk)
        serialized_data = TypeClothingSerializerForStaff(type_1, context={'request': self.request})
        validated_data = serialized_data.data
        validated_data['get_color_list'] = type_1.get_color_list()
        validated_data['get_size_list'] = type_1.get_size_list()
        validated_data['views'] = type_1.views
        validated_data['description'] = type_1.name = 'DESCRIPTION'

        serialized_data.update(instance=type_1, validated_data=validated_data)
        type_1.refresh_from_db()
        self.assertEqual(type_1.description, 'DESCRIPTION')

    def test_update_characteristics(self):
        type_1 = TypeClothing.objects.get(pk=choice(Product.objects.filter(is_published=True)).type.pk)
        serialized_data = TypeClothingSerializerForStaff(type_1, context={'request': self.request})
        validated_data = serialized_data.data
        validated_data['get_color_list'] = type_1.get_color_list()
        validated_data['get_size_list'] = type_1.get_size_list()
        validated_data['views'] = type_1.views
        validated_data['characteristics'] = type_1.name = 'characteristics'.upper()

        serialized_data.update(instance=type_1, validated_data=validated_data)
        type_1.refresh_from_db()
        self.assertEqual(type_1.characteristics, 'characteristics'.upper())

    def test_update_delivery(self):
        type_1 = TypeClothing.objects.get(pk=choice(Product.objects.filter(is_published=True)).type.pk)
        serialized_data = TypeClothingSerializerForStaff(type_1, context={'request': self.request})
        validated_data = serialized_data.data
        validated_data['get_color_list'] = type_1.get_color_list()
        validated_data['get_size_list'] = type_1.get_size_list()
        validated_data['views'] = type_1.views
        validated_data['delivery'] = type_1.name = 'delivery'.upper()

        serialized_data.update(instance=type_1, validated_data=validated_data)
        type_1.refresh_from_db()
        self.assertEqual(type_1.delivery, 'delivery'.upper())


class TypeClothingListSerializerForStaffTest(TestCase):
    fixtures = ['test_db.json']

    @classmethod
    def setUpTestData(cls):
        cls.type_1 = choice(TypeClothing.objects.all())
        cls.type_2 = choice(TypeClothing.objects.all())
        cls.type_3 = choice(TypeClothing.objects.all())
        cls.request = APIRequestFactory().get(reverse('type-detail', kwargs={'slug': cls.type_1.slug}))

    def test_field_presence(self):
        type_data = TypeClothingListSerializerForStaff(
                                            choice(Product.objects.filter(is_published=True)).type.product_set.all(),
                                            context={'request': self.request}).data
        self.assertCountEqual(list(type_data.keys()), ['id', 'url', 'views', 'name', 'description', 'products',
                                                       'characteristics', 'delivery', 'color_list', 'size_list'])
        self.assertCountEqual(list(type_data['products'][0].keys()), ['name', 'photo', 'url', 'collection', 'price',
                                                         'color_list', 'size_list'])

    def test_data(self):
        data = {'id': self.type_1.pk,
                'views': self.type_1.views,
                'url': f'http://testserver/api/v1/type/{self.type_1.slug}',
                'name': self.type_1.type,
                'description': self.type_1.description,
                'characteristics': self.type_1.characteristics,
                'delivery': self.type_1.delivery,
                'color_list': self.type_1.get_color_list(),
                'size_list': self.type_1.get_size_list(),
                }
        if self.type_1.product_set.all():
            data['products'] = ProductSerializerForTypeClothing(self.type_1.product_set.all(), many=True,
                                                                context={'request': self.request}).data
        else:
            data['products'] = []
        self.assertEqual(TypeClothingSerializerForStaff(self.type_1, context={'request': self.request}).data, data)

    def test_many_data(self):
        data = [{'id': self.type_1.pk,
                'views': self.type_1.views,
                 'url': f'http://testserver/api/v1/type/{self.type_1.slug}',
                 'name': self.type_1.type,
                 'description': self.type_1.description,
                 'characteristics': self.type_1.characteristics,
                 'delivery': self.type_1.delivery,
                 'color_list': self.type_1.get_color_list(),
                 'size_list': self.type_1.get_size_list(),
                 },
                {'id': self.type_2.pk,
                 'views': self.type_2.views,
                 'url': f'http://testserver/api/v1/type/{self.type_2.slug}',
                 'name': self.type_2.type,
                 'description': self.type_2.description,
                 'characteristics': self.type_2.characteristics,
                 'delivery': self.type_2.delivery,
                 'color_list': self.type_2.get_color_list(),
                 'size_list': self.type_2.get_size_list(),
                 },
                {'id': self.type_3.pk,
                 'views': self.type_3.views,
                 'url': f'http://testserver/api/v1/type/{self.type_3.slug}',
                 'name': self.type_3.type,
                 'description': self.type_3.description,
                 'characteristics': self.type_3.characteristics,
                 'delivery': self.type_3.delivery,
                 'color_list': self.type_3.get_color_list(),
                 'size_list': self.type_3.get_size_list(),
                 },
                ]
        types = [self.type_1, self.type_2, self.type_3]
        for type_clothing_id in range(3):
            if types[type_clothing_id].product_set.all():
                data[type_clothing_id]['products'] = ProductSerializerForTypeClothing(list(
                                                               types[type_clothing_id].product_set.all()), many=True,
                                                               context={'request': self.request}).data
            else:
                data[type_clothing_id]['products'] = list()
        self.assertEqual(TypeClothingSerializerForStaff([self.type_1, self.type_2, self.type_3],
                                                        context={'request': self.request}, many=True).data, data)


class CollectionSerializerForStaffTest(TestCase):
    fixtures = ['test_db.json']

    @classmethod
    def setUpTestData(cls):
        cls.collection_1 = choice(Collection.objects.all())
        cls.collection_2 = choice(Collection.objects.all())
        cls.collection_3 = choice(Collection.objects.all())
        cls.request = APIRequestFactory().get(reverse('collection-detail', kwargs={'slug': cls.collection_1.slug}))

    def test_field_presence(self):
        collection_data = CollectionSerializerForStaff(self.collection_1, context={'request': self.request}).data
        self.assertCountEqual(list(collection_data.keys()), ['id', 'name', 'description', 'is_published', 'slug',
                                                             'views', 'products'])
        self.assertCountEqual(list(collection_data['products'][0].keys()), ['name', 'photo', 'url', 'type', 'price',
                                                                            'color_list', 'size_list'])

    def test_data(self):
        data = {
                'id': self.collection_1.pk,
                'name': self.collection_1.name,
                'description': self.collection_1.description,
                'is_published': self.collection_1.is_published,
                'slug': self.collection_1.slug,
                'views': self.collection_1.views,
                'products': ProductSerializerForCollection(self.collection_1.product_set, many=True,
                                                           context={'request': self.request}).data
                }
        self.assertEqual(CollectionSerializerForStaff(self.collection_1, context={'request': self.request}).data, data)

    def test_many_data(self):
        data = [{'id': self.collection_1.pk,
                 'name': self.collection_1.name,
                 'description': self.collection_1.description,
                 'is_published': self.collection_1.is_published,
                 'slug': self.collection_1.slug,
                 'views': self.collection_1.views,
                 'products': ProductSerializerForCollection(self.collection_1.product_set, many=True,
                                                            context={'request': self.request}).data
                 },
                {'id': self.collection_2.pk,
                 'name': self.collection_2.name,
                 'description': self.collection_2.description,
                 'is_published': self.collection_2.is_published,
                 'slug': self.collection_2.slug,
                 'views': self.collection_2.views,
                 'products': ProductSerializerForCollection(self.collection_2.product_set, many=True,
                                                            context={'request': self.request}).data
                 },
                {'id': self.collection_3.pk,
                 'name': self.collection_3.name,
                 'description': self.collection_3.description,
                 'is_published': self.collection_3.is_published,
                 'slug': self.collection_3.slug,
                 'views': self.collection_3.views,
                 'products': ProductSerializerForCollection(self.collection_3.product_set, many=True,
                                                            context={'request': self.request}).data
                 },
                ]
        self.assertEqual(CollectionSerializerForStaff([self.collection_1, self.collection_2, self.collection_3],
                                                      context={'request': self.request}, many=True).data, data)

    def test_update_name(self):
        serialized_data = CollectionSerializerForStaff(self.collection_1, context={'request': self.request})
        validated_data = serialized_data.data
        validated_data['views'] = self.collection_1.views
        validated_data['name'] = 'name'.upper()
        serialized_data.update(instance=self.collection_1, validated_data=validated_data)
        self.collection_1.refresh_from_db()
        self.assertEqual(self.collection_1.name, 'name'.upper())

    def test_update_description(self):
        serialized_data = CollectionSerializerForStaff(self.collection_1, context={'request': self.request})
        validated_data = serialized_data.data
        validated_data['views'] = self.collection_1.views
        validated_data['description'] = 'description'.upper()
        serialized_data.update(instance=self.collection_1, validated_data=validated_data)
        self.collection_1.refresh_from_db()
        self.assertEqual(self.collection_1.description, 'description'.upper())

    def test_update_is_published(self):
        serialized_data = CollectionSerializerForStaff(self.collection_1, context={'request': self.request})
        validated_data = serialized_data.data
        validated_data['views'] = self.collection_1.views
        validated_data['is_published'] = False
        serialized_data.update(instance=self.collection_1, validated_data=validated_data)
        self.collection_1.refresh_from_db()
        self.assertFalse(self.collection_1.is_published)
        for product in self.collection_1.product_set.all():
            self.assertFalse(product.is_published)

    def test_update_slug(self):
        serialized_data = CollectionSerializerForStaff(self.collection_1, context={'request': self.request})
        validated_data = serialized_data.data
        validated_data['views'] = self.collection_1.views
        validated_data['name'] = 'slug'
        validated_data['slug'] = 'slug'
        serialized_data.update(instance=self.collection_1, validated_data=validated_data)
        self.collection_1.refresh_from_db()
        self.assertEqual(self.collection_1.slug, 'slug')


class CollectionSerializerForProductSerializerStaffTest(TestCase):
    fixtures = ['test_db.json']

    @classmethod
    def setUpTestData(cls):
        cls.collection_1 = choice(Collection.objects.all())
        cls.collection_2 = choice(Collection.objects.all())
        cls.collection_3 = choice(Collection.objects.all())
        cls.request = APIRequestFactory().get(reverse('collection-detail', kwargs={'slug': cls.collection_1.slug}))

    def test_field_presence(self):
        collection_data = CollectionSerializerForProductSerializerStaff(self.collection_1,
                                                                        context={'request': self.request}).data
        self.assertCountEqual(list(collection_data.keys()), ['id', 'name', 'url', 'description'])

    def test_data(self):
        data = {'id': self.collection_1.pk,
                'url': f'http://testserver/api/v1{self.collection_1.get_absolute_url()}',
                'name': self.collection_1.name,
                'description': self.collection_1.description}
        self.assertEqual(CollectionSerializerForProductSerializerStaff(self.collection_1,
                                                                       context={'request': self.request}).data, data)


class TypeClothingSerializerForProductSerializerStaffTest(TestCase):
    fixtures = ['test_db.json']

    @classmethod
    def setUpTestData(cls):
        cls.type_1 = choice(TypeClothing.objects.all())
        cls.type_2 = choice(TypeClothing.objects.all())
        cls.type_3 = choice(TypeClothing.objects.all())
        cls.request = APIRequestFactory().get(reverse('type-detail', kwargs={'slug': cls.type_1.slug}))

    def test_field_presence(self):
        type_data = TypeClothingSerializerForProductSerializerStaff(
            choice(Product.objects.filter(is_published=True)).type,
            context={'request': self.request}).data
        self.assertCountEqual(list(type_data.keys()), ['name', 'url', 'description', 'characteristics', 'delivery'])

    def test_data(self):
        data = {'name': self.type_1.type,
                'url': f'http://testserver/api/v1/type/{self.type_1.slug}',
                'description': self.type_1.description,
                'characteristics': self.type_1.characteristics,
                'delivery': self.type_1.delivery,
                }
        self.assertEqual(TypeClothingSerializerForProductSerializerStaff(self.type_1, context={'request': self.request},
                                                                         ).data, data)

    def test_many_data(self):
        data = [{'name': self.type_1.type,
                 'url': f'http://testserver/api/v1/type/{self.type_1.slug}',
                 'description': self.type_1.description,
                 'characteristics': self.type_1.characteristics,
                 'delivery': self.type_1.delivery,
                },
                {'name': self.type_2.type,
                 'url': f'http://testserver/api/v1/type/{self.type_2.slug}',
                 'description': self.type_2.description,
                 'characteristics': self.type_2.characteristics,
                 'delivery': self.type_2.delivery,
                 },
                {'name': self.type_3.type,
                 'url': f'http://testserver/api/v1/type/{self.type_3.slug}',
                 'description': self.type_3.description,
                 'characteristics': self.type_3.characteristics,
                 'delivery': self.type_3.delivery,
                 },
                ]
        self.assertEqual(TypeClothingSerializerForProductSerializerStaff([self.type_1, self.type_2, self.type_3],
                                                                         context={'request': self.request},
                                                                         many=True).data, data)


class ProductSerializerForStaffTest(TestCase):
    fixtures = ['test_db.json']

    @classmethod
    def setUpTestData(cls):
        cls.product_1 = choice(Product.objects.all())
        cls.product_2 = choice(Product.objects.all())
        cls.product_3 = choice(Product.objects.all())
        cls.request = APIRequestFactory().get(reverse('product-detail',
                                                      kwargs={'collection_slug': cls.product_1.collection.slug,
                                                              'slug': cls.product_1.slug}))

    def test_field_presence(self):
        product_data = ProductSerializerForStaff(self.product_1, context={'request': self.request}).data
        self.assertCountEqual(list(product_data.keys()), ['id', 'name', 'slug', 'url', 'collection', 'price', 'photo',
                                                          'is_published', 'description_print', 'size_list',
                                                          'color_list', 'type', 'time_create', 'time_update', 'views'])

    def test_data(self):
        data = {'id': self.product_1.pk,
                'name': self.product_1.name,
                'slug': self.product_1.slug,
                'url': f'http://testserver/api/v1{self.product_1.get_absolute_url()}',
                'collection': {'id': self.product_1.collection.pk,
                               'name': self.product_1.collection.name,
                               'url': f'http://testserver/api/v1/catalog/{self.product_1.collection.slug}',
                               'description': self.product_1.collection.description},
                'type': {'name': self.product_1.type.type,
                         'url': f'http://testserver/api/v1/type/{self.product_1.type.slug}',
                         'description': self.product_1.type.description,
                         'characteristics': self.product_1.type.characteristics,
                         'delivery': self.product_1.type.delivery
                         },
                'photo': f'http://testserver{self.product_1.photo.url}',
                'price': self.product_1.price,
                'is_published': True,
                'description_print': self.product_1.description_print,
                'color_list': self.product_1.get_color_list(),
                'size_list': self.product_1.get_size_list(),
                'time_create': datetime.strftime(self.product_1.time_create, '%Y-%m-%dT%H:%M:%S.%fZ'),
                'time_update': datetime.strftime(self.product_1.time_update, '%Y-%m-%dT%H:%M:%S.%fZ'),
                'views': self.product_1.views
                }
        self.assertCountEqual(ProductSerializerForStaff(self.product_1, context={'request': self.request}).data, data)

    def test_update_external_key_collection(self):
        serialized_product = ProductSerializerForStaff(self.product_1, context={'request': self.request})
        validated_data = serialized_product.data
        validated_data['type']['type'] = validated_data['type']['name']
        validated_data['collection']['name'] = self.product_2.collection.name
        validated_data['views'] = self.product_1.views
        serialized_product.update(self.product_1, validated_data)
        self.assertEqual(self.product_1.collection, self.product_2.collection)

    def test_update_external_key_type(self):
        serialized_product = ProductSerializerForStaff(self.product_1, context={'request': self.request})
        validated_data = serialized_product.data
        validated_data['type']['type'] = self.product_2.type.type
        validated_data['views'] = self.product_1.views
        serialized_product.update(self.product_1, validated_data)
        self.assertEqual(self.product_1.type, self.product_2.type)
