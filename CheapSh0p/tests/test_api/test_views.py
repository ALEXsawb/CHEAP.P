import unittest
from random import choice

from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory, APIClient

from API_online_store.pagination import TypeClothingListAPIPagination
from API_online_store.serializers import *
from API_online_store.serializers.for_staff import *
from online_store.models import Product, Collection, TypeClothing, Orders
from online_store.services.collections import splitting_products_by_row
from API_online_store.utils import get_types_products
from django.forms.models import model_to_dict


class LoginMixin:
    @staticmethod
    def get_login_client():
        User.objects.create_superuser(username='TestSuperUser', email='super@user.com', password='SuperUser321')
        user = User.objects.get(username='TestSuperUser')
        client = APIClient()
        client.force_authenticate(user=user)
        return client


class CatalogAPITest(TestCase):
    fixtures = ['test_db.json', ]

    def test_data(self):
        response = self.client.get(reverse('catalog-list'))
        products = Product.objects.select_related('collection', 'type').order_by('-collection__pk')
        products_by_collections = splitting_products_by_row(products)
        request = APIRequestFactory().get(reverse('catalog-list'), format='json')
        catalog = CatalogSerializer(products_by_collections, many=True, context={'request': request})
        self.assertEqual(response.data['results'], catalog.data[:5:])
        self.assertEqual(response.data['count'], len(catalog.data))


class CollectionAPITest(LoginMixin, TestCase):
    fixtures = ['test_db.json']

    def setUp(self) -> None:
        self.collection = choice(Collection.objects.all())

    def test_data(self):
        request = APIRequestFactory().get(reverse('collection-detail', kwargs={'slug': self.collection.slug}))
        response = self.client.get(reverse('collection-detail', kwargs={'slug': self.collection.slug}))
        self.assertEqual(response.data, CollectionSerializer(self.collection, context={'request': request}).data)

    def test_data_with_staff_access(self):
        client = self.get_login_client()
        request = APIRequestFactory().get(reverse('collection-detail', kwargs={'slug': self.collection.slug}))
        response = client.get(reverse('collection-detail', kwargs={'slug': self.collection.slug}))
        self.assertEqual(response.data,
                         CollectionSerializerForStaff(self.collection, context={'request': request}).data)

    def test_update_name(self):
        client = self.get_login_client()
        data = model_to_dict(self.collection)
        data['name'] = 'name name name'
        response = client.put(reverse('collection-detail', kwargs={'slug': self.collection.slug}), data=data)
        collection = Collection.objects.get(pk=self.collection.pk)
        self.assertEquals(response.data['name'], collection.name, collection.slug)
        self.assertEqual(response.data['name'], data['name'])

    @unittest.expectedFailure
    def test_update_slug(self):
        client = self.get_login_client()
        data = model_to_dict(self.collection)
        data['slug'] = 'name-name-name'
        data['url'] = 'name-name-name'
        response = client.put(reverse('collection-detail', kwargs={'slug': self.collection.slug}), data=data)
        collection = Collection.objects.get(pk=self.collection.pk)
        self.assertEquals(response.data['slug'], data['slug'], collection.slug)

    def test_update_views(self):
        client = self.get_login_client()
        data = model_to_dict(self.collection)
        data['views'] = 100
        response = client.put(reverse('collection-detail', kwargs={'slug': self.collection.slug}), data=data)
        collection = Collection.objects.get(pk=self.collection.pk)
        self.assertEquals(response.data['views'], collection.views, data['views'])

    def test_update_description(self):
        client = self.get_login_client()
        data = model_to_dict(self.collection)
        data['description'] = 'DESCRIPTION'
        response = client.put(reverse('collection-detail', kwargs={'slug': self.collection.slug}), data=data)
        collection = Collection.objects.get(pk=self.collection.pk)
        self.assertEquals(response.data['description'], collection.description, data['description'])

    def test_update_description(self):
        client = self.get_login_client()
        data = model_to_dict(self.collection)
        data['is_published'] = False
        response = client.put(reverse('collection-detail', kwargs={'slug': self.collection.slug}), data=data)
        collection = Collection.objects.get(pk=self.collection.pk)
        self.assertEquals(response.data['is_published'], collection.is_published, data['is_published'])

    @unittest.expectedFailure
    def access_to_unsafe_method_for_user(self):
        data = model_to_dict(self.collection)
        data['name'] = 'name name name'
        response = self.client.put(reverse('collection-detail', kwargs={'slug': self.collection.slug}), data=data)
        self.assertEqual(response.status_code, 200)


class ProductAPITest(LoginMixin, TestCase):
    fixtures = ['test_db.json']

    def setUp(self) -> None:
        self.product = choice(Product.objects.select_related('collection').all())
        self.request = APIRequestFactory().get(reverse('product-detail',
                                                       kwargs={'collection_slug': self.product.collection.slug,
                                                               'slug': self.product.slug}))
        self.data = ProductSerializerForStaff(self.product, context={'request': self.request}).data
        self.data.pop('photo')

    def test_data(self):
        request = APIRequestFactory().get(reverse('product-detail',
                                                  kwargs={'collection_slug': self.product.collection.slug,
                                                          'slug': self.product.slug}))
        response = self.client.get(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                     'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, ProductSerializer(self.product, context={'request': request}).data)

    def test_data_with_staff_access(self):
        client = self.get_login_client()
        request = APIRequestFactory().get(reverse('product-detail',
                                                  kwargs={'collection_slug': self.product.collection.slug,
                                                          'slug': self.product.slug}))
        response = client.get(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, ProductSerializerForStaff(self.product, context={'request': request}).data)

    def test_update_name(self):
        self.data['name'] = 'name name name'
        client = self.get_login_client()
        response = client.put(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                'slug': self.product.slug}),
                              data=self.data, format="json")
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['name'], product.name, product.slug)
        self.assertEqual(response.data['name'], self.data['name'])

    @unittest.expectedFailure
    def test_update_slug(self):
        self.data['slug'] = 'name-name-name'
        client = self.get_login_client()
        response = client.put(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                'slug': self.product.slug}),
                              data=self.data, format="json")
        product = Product.objects.get(pk=self.product.pk)
        self.assertEquals(response.data['slug'], self.data['slug'], product.slug)

    def test_update_views(self):
        view = 100
        self.data['views'] = view + 100
        client = self.get_login_client()
        response = client.put(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                'slug': self.product.slug}),
                              data=self.data, format="json")
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['views'], product.views, self.data['views'])

    def test_update_description(self):
        client = self.get_login_client()
        self.data['description_print'] = 'DESCRIPTION'
        response = client.put(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                'slug': self.product.slug}),
                              data=self.data, format="json")
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['description_print'], product.description_print, self.data['description_print'])

    def test_update_is_published(self):
        client = self.get_login_client()
        self.data['is_published'] = False
        response = client.put(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                'slug': self.product.slug}),
                              data=self.data, format="json")
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['is_published'], product.is_published, self.data['is_published'])

    @unittest.expectedFailure
    def access_to_unsafe_method_for_user(self):
        data = ProductSerializerForStaff(self.product, context={'request': self.request}).data
        data['name'] = 'name name name'
        product = self.client.put(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                    'slug': self.product.slug}), data=data)
        self.assertEqual(product.status_code, 200)

    def test_update_collection(self):
        client = self.get_login_client()
        collection = choice(Collection.objects.all())
        self.data['collection']['name'] = collection.name
        response = client.put(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                'slug': self.product.slug}),
                              data=self.data, format="json")
        product = Product.objects.filter(collection__pk=collection.pk)[0]
        self.assertEqual(response.status_code, 200)
        collection_form_response = Collection.objects.get(slug=response.data['collection']['url'].split('/')[-1])
        self.assertEquals(collection_form_response.pk, product.collection.pk, self.data['collection'])

    def test_update_collection_and_update_something_else(self):
        client = self.get_login_client()
        collection = choice(Collection.objects.all())
        self.data['collection']['name'] = collection.name
        self.data['name'] = '123'
        response = client.put(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                'slug': self.product.slug}),
                              data=self.data, format="json")
        product = Product.objects.filter(collection__pk=collection.pk)[0]
        self.assertEqual(response.status_code, 200)
        collection_form_response = Collection.objects.get(slug=response.data['collection']['url'].split('/')[-1])
        self.assertEquals(collection_form_response.pk, product.collection.pk, self.data['collection'])
        self.assertEquals(response.data['name'], self.data['name'], '123')

    def test_update_type_and_update_something_else(self):
        client = self.get_login_client()
        new_product_type = choice(TypeClothing.objects.all())
        self.data['type']['name'] = new_product_type.type
        self.data['name'] = '123'
        response = client.put(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                'slug': self.product.slug}),
                              data=self.data, format="json")
        self.assertEqual(response.status_code, 200)
        type_form_response = TypeClothing.objects.get(slug=response.data['type']['url'].split('/')[-1])
        self.assertEquals(type_form_response.pk, new_product_type.pk)
        self.assertEquals(response.data['name'], self.data['name'], '123')

    def test_delete(self):
        Orders.objects.all().delete()
        quantity_products = Product.objects.all().count()
        client = self.get_login_client()
        response = client.delete(reverse('product-detail', kwargs={'collection_slug': self.product.collection.slug,
                                                                   'slug': self.product.slug}))

        self.assertEqual(response.status_code, 204)
        self.assertEqual(quantity_products-1, Product.objects.all().count())


class TypeClothingAPITest(LoginMixin, TestCase):
    fixtures = ['test_db.json']

    def setUp(self) -> None:
        self.type = choice(TypeClothing.objects.all())
        self.request = APIRequestFactory().get(reverse('type-detail', kwargs={'slug': self.type.slug}))
        self.data = TypeClothingSerializerForStaff(self.type, context={'request': self.request}).data

    def test_data(self):
        request = APIRequestFactory().get(reverse('type-detail', kwargs={'slug': self.type.slug}))
        response = self.client.get(reverse('type-detail', kwargs={'slug': self.type.slug}))
        self.assertEqual(response.data, TypeClothingSerializer(self.type, context={'request': request}).data)

    def test_data_with_staff_access(self):
        client = self.get_login_client()
        request = APIRequestFactory().get(reverse('type-detail', kwargs={'slug': self.type.slug}))
        response = client.get(reverse('type-detail', kwargs={'slug': self.type.slug}))
        self.assertEqual(response.data, TypeClothingSerializerForStaff(self.type, context={'request': request}).data)

    def test_update_name(self):
        client = self.get_login_client()
        self.data['name'] = 'name name name'
        response = client.put(reverse('type-detail', kwargs={'slug': self.type.slug}), data=self.data, format='json')
        type_clothing = TypeClothing.objects.get(pk=self.type.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['name'], type_clothing.type, type_clothing.slug)
        self.assertEqual(response.data['name'], self.data['name'])

    @unittest.expectedFailure
    def test_update_slug(self):
        client = self.get_login_client()
        self.data['slug'] = 'name-name-name'
        response = client.put(reverse('type-detail', kwargs={'slug': self.type.slug}), data=self.data, format='json')
        type_clothing = TypeClothing.objects.get(pk=self.type.pk)
        self.assertEquals(response.data['slug'], self.data['slug'], type_clothing.slug)

    def test_update_views(self):
        client = self.get_login_client()
        self.data['views'] = 100
        response = client.put(reverse('type-detail', kwargs={'slug': self.type.slug}), data=self.data, format='json')
        type_clothing = TypeClothing.objects.get(pk=self.type.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['views'], type_clothing.views, self.data['views'])

    def test_update_description(self):
        client = self.get_login_client()
        self.data['description'] = 'DESCRIPTION'
        response = client.put(reverse('type-detail', kwargs={'slug': self.type.slug}), data=self.data, format='json')
        type_clothing = TypeClothing.objects.get(pk=self.type.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['description'], type_clothing.description, self.data['description'])

    def test_update_characteristics(self):
        client = self.get_login_client()
        self.data['characteristics'] = 'CHARACTERISTICS'
        response = client.put(reverse('type-detail', kwargs={'slug': self.type.slug}), data=self.data, format='json')
        type_clothing = TypeClothing.objects.get(pk=self.type.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['characteristics'], type_clothing.characteristics, self.data['characteristics'])

    def test_update_delivery(self):
        client = self.get_login_client()
        self.data['delivery'] = '20-30 days'
        response = client.put(reverse('type-detail', kwargs={'slug': self.type.slug}), data=self.data, format='json')
        type_clothing = TypeClothing.objects.get(pk=self.type.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['delivery'], type_clothing.delivery, self.data['delivery'])

    def test_update_sizes(self):
        client = self.get_login_client()
        self.data['size_list'] = ['S', 'M', 'XL']
        response = client.put(reverse('type-detail', kwargs={'slug': self.type.slug}), data=self.data, format='json')
        type_clothing = TypeClothing.objects.get(pk=self.type.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['size_list'], type_clothing.get_size_list(), self.data['size_list'])

    def test_update_colors(self):
        client = self.get_login_client()
        self.data['color_list'] = ['white']
        response = client.put(reverse('type-detail', kwargs={'slug': self.type.slug}), data=self.data, format='json')
        type_clothing = TypeClothing.objects.get(pk=self.type.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.data['color_list'], type_clothing.get_color_list(), self.data['color_list'])
        for product in type_clothing.product_set.all():
            if product.color not in response.data['color_list']:
                self.assertFalse(product.is_published)


class TypeClothingListAPITest(LoginMixin, TestCase):
    fixtures = ['test_db.json']

    @staticmethod
    def get_products_by_type():
        return get_types_products(Product.objects.filter(is_published=True).select_related('type', 'collection'
                                                                                           ).order_by('-type__pk', ))

    def test_data(self):
        request = APIRequestFactory().get(reverse('types-list'))
        response = self.client.get(reverse('types-list'))
        products_by_type = self.get_products_by_type()
        data = TypeClothingListSerializer(list(products_by_type.values()), many=True,
                                          context={'request': request}).data
        for index in range(len(response.data['results'])):
            self.assertCountEqual(response.data['results'][index].pop('products'), data[index].pop('products'))
            self.assertEqual(response.data['results'][index], data[index])

    def test_data_with_staff_access(self):
        client = self.get_login_client()
        request = APIRequestFactory().get(reverse('types-list'))
        response = client.get(reverse('types-list'))
        products_by_type = self.get_products_by_type()
        id_types_with_products = list(products_by_type.keys())
        types_without_products = list(TypeClothing.objects.filter(~Q(pk__in=id_types_with_products)))
        data = TypeClothingListSerializerForStaff(list(products_by_type.values())+types_without_products, many=True,
                                                  context={'request': request}).data
        products_by_types_id = []
        for index in range(5):
            self.assertCountEqual(response.data['results'][index].pop('products'), data[index]['products'])
            products_by_types_id.append({'id': data[index]['id'], 'products': data[index].pop('products')})
            self.assertEqual(response.data['results'][index], data[index])
        number_type_on_next_page = 0
        full_page = 0
        for products_by_type_id in products_by_types_id:
            if not products_by_type_id['products']:
                number_type = (data.index(products_by_type_id)+1)
                full_page = number_type//5
                number_type_on_next_page = number_type % 5
                break
        if full_page:
            if number_type:
                full_page += 1
            response = client.get(reverse('types-list'), {'page': full_page})
            self.assertEqual(response.status_code, 200)
            self.assertIn(response.data['results'][number_type_on_next_page], data)
