import json
import os
import random
import shutil
from ast import literal_eval
from random import choice
from django.test import TestCase
from django.db.models.aggregates import Max
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from CheapSh0p import settings
from online_store.forms import SendEmailForm
from online_store.models import *
from online_store.services.basket import add_product_in_basket_or_update_data
from online_store.services.collections import get_max_price_catalog, get_catalog


# 114 стр после добавления мидлвеер вернутся
from online_store.services.filters import get_Q_for_collections_page


class DeleteCacheFilesMixin:
    def setUp(self):
        self.delete_all_fields_from_cache_directory()

    @staticmethod
    def delete_all_fields_from_cache_directory():
        cache_dir_path = str(settings.BASE_DIR) + '/cache'
        if os.path.isdir(os.path.realpath(cache_dir_path)):
            shutil.rmtree(cache_dir_path)


class PaginationMixin:

    @staticmethod
    def get_number_all_pages(response):
        return str(response.context['page_obj']).split(' ')[-1][:-1:]

    @staticmethod
    def get_page_number(response):
        return str(response.context['page_obj']).split(' ')[1]


class CheapSh0peHomeTest(DeleteCacheFilesMixin, TestCase):
    fixtures = ['test_db.json', ]

    def test_explicitly_specified_path_exists_and_works(self):
        self.assertEqual(self.client.get('').status_code, 200)

    def test_for_existence_and_operation_named_path(self):
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)

    def test_get_context_data_method(self):
        response = self.client.get(path=reverse('home'))
        hot_collection = response.context['hot_collection']

        self.assertEqual(Collection.objects.aggregate(Max('views'))['views__max'],
                         hot_collection.views)

        self.assertEqual(Collection.objects.order_by('-views')[0], hot_collection)

        self.assertEqual(list(hot_collection.product_set.all()), list(response.context['hot_collection_products']))

        self.assertCountEqual(list(response.context['top_clothing']),
                              list(Product.objects.order_by('-views')[:4]))

        self.assertEqual(response.context['css'], 'home.css')

    def test_template_name_attribute(self):
        response = self.client.get(path='/')
        print(response.status_code)
        self.assertTemplateUsed(response, 'online_store/home.html')


class CheapSh0peProductTest(DeleteCacheFilesMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        list_colors = ['white', 'black']
        Collection.objects.create(name=f'test collection 1',
                                  description='test_collection_description',
                                  views=1)
        TypeClothing.objects.create(type=f'test_type_1', description='test_type_description',
                                    characteristics='test_characteristics', colors='black, white',
                                    delivery='7 - 14 day', size='S, M, XL',
                                    slug=f'test-type-slug-1',
                                    views=1)
        for number in range(1, 4):
            Product.objects.create(collection=Collection.objects.last(), name=f'product {number}',
                                   type=TypeClothing.objects.last(), price=20+number,
                                   color=choice(list_colors), description_print='description_print_test',
                                   views=20+number)

    def test_url(self):
        product = choice(Product.objects.all())
        self.assertEqual(self.client.get(f'/catalog/{product.collection.slug}/{product.slug}').status_code, 200)
        client_from_reverse_path = self.client.get(path=reverse('product',
                                                                kwargs={'collection_slug':
                                                                        Collection.objects.last().slug,
                                                                        'product_slug':
                                                                        product.slug}))
        self.assertEqual(client_from_reverse_path.status_code, 200)

    def test_context_data(self):
        product = choice(Product.objects.all())
        product_views_before_request = product.views
        type_views_before_request = product.type.views

        response = self.client.get(f'/catalog/{product.collection.slug}/{product.slug}')

        self.assertEqual(response.context['product'], product)
        self.assertEqual(response.context['css'], 'product_card.css')
        self.assertEqual(product_views_before_request+1, Product.objects.get(pk=product.pk).views)
        self.assertEqual(type_views_before_request+1, TypeClothing.objects.last().views)

    def test_template_name(self):
        collection = Collection.objects.last()
        products = collection.get_products_this_collection()
        response = self.client.get(path=reverse('product',
                                                kwargs={'collection_slug': collection.slug,
                                                        'product_slug': choice(products).slug}))
        self.assertTemplateUsed(response, 'online_store/product_card.html')

    def test_post_method(self):
        data = {'add_size': ['M'], 'add_color': ['black'], 'product_id': ['7']}
        request = self.client.post(data=data, path=reverse('product',
                                                           kwargs={'collection_slug': Collection.objects.last().slug,
                                                                   'product_slug': choice(Product.objects.all()).slug}))
        self.assertIn(request.status_code, [302, 303, 304])
        self.assertEqual(literal_eval(self.client.cookies['basket'].coded_value),
                         '{"7": [{"color": "black", "size": "M", "quantity": 1}]}')


class CheapSh0peCatalogTest(DeleteCacheFilesMixin, PaginationMixin, TestCase):
    fixtures = ['test_db.json', ]

    def test_url(self):
        self.assertEqual(self.client.get('/catalog').status_code, 200)
        self.assertEqual(self.client.get(path=reverse('catalog')).status_code, 200)

    def test_context_data(self):
        response = self.client.get(path=reverse('catalog'))
        self.assertEqual(list(response.context['all_public_collections']),
                         list(Collection.objects.filter(is_published=True).order_by('-pk')))
        self.assertEqual(response.context['css'], 'catalog.css')
        self.assertEqual(float(response.context['max_product_price']),
                         float(Product.objects.order_by('-price')[0].price))

    def test_template_name(self):
        self.assertTemplateUsed(self.client.get(path=reverse('catalog')), 'online_store/catalog.html')

    def test_pagination_first_page(self):
        response = self.client.get(path=reverse('catalog'))
        paginated_by = 3

        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['object_list']), paginated_by)

        number_of_pages = len(response.context['all_public_collections'])//3
        if len(response.context['all_public_collections']) % paginated_by:
            number_of_pages += 1

        self.assertEqual(self.get_number_all_pages(response), str(number_of_pages))

    def test_pagination_second_page(self):
        response = self.client.get(reverse('catalog'), {'page': '2'})
        self.assertEqual([8, 7, 6], [collection_products[0].collection.pk for collection_products
                                     in response.context['object_list']])

        self.assertEqual(self.get_page_number(response), str(2))


class CheapSh0peCollectionTest(DeleteCacheFilesMixin, TestCase):
    fixtures = ['test_db.json', ]

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.slugs = Collection.objects.all().values_list('slug', flat=True)
        super().setUpClass(*args, **kwargs)

    def test_url(self):
        slug = choice(self.slugs)
        self.assertEqual(self.client.get(fr'/catalog/{slug}').status_code, 200)
        self.assertEqual(self.client.get(reverse('collection', kwargs={'collection_slug': slug})).status_code, 200)

    def test_template_name(self):
        slug = choice(self.slugs)
        self
        response = self.client.get(reverse('collection', kwargs={'collection_slug': slug}))
        self.assertTemplateUsed(response, 'online_store/collection.html')

    def test_context_data(self):
        slug = choice(self.slugs)
        response = self.client.get(reverse('collection', kwargs={'collection_slug': slug}))
        collection = Collection.objects.get(slug=slug)
        self.assertCountEqual(list(response.context['collection']), list(collection.get_products_this_collection()))
        self.assertEqual(list(response.context['all_public_collections']),
                         list(Collection.objects.filter(is_published=True).order_by('-pk')))
        self.assertEqual(response.context['css'], 'catalog.css')


class CheapSh0peCollectionsTest(DeleteCacheFilesMixin, PaginationMixin, TestCase):
    fixtures = ['test_db.json', ]

    def __init__(self, *args, **kwargs):
        self.delete_all_fields_from_cache_directory()
        self.max_price = get_max_price_catalog(get_catalog())
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_number_pages_by_sorted_products(sorted_products):
        number_pages = len(sorted_products) // 9
        if len(sorted_products) % 9:
            number_pages += 1
        return number_pages

    @staticmethod
    def get_catalog_by_page(page: int, products: list, ) -> list:
        catalog = []
        for_this_number_of_products_more = (page - 1) * 9
        number_product_in_row = 3

        start_ = 3 + for_this_number_of_products_more
        end_ = 12 + for_this_number_of_products_more
        for row_limiter in range(start_, end_, 3):
            products_row = products[row_limiter - number_product_in_row:row_limiter:]
            if products_row:
                catalog.append(products_row)
        return catalog

    def test_url(self):
        response = self.client.post('/catalog/collections', data={'color__black': ['on'],
                                                                  'type__hoodie': ['on'],
                                                                  'min_price': ['0'],
                                                                  'max_price': ['50.58'],
                                                                  'collection__red&black 2': ['on'],
                                                                  'collection__red&black': ['on'],
                                                                  'collection__neon hoodie': ['on']})
        self.assertEqual(response.status_code, 200)

    def test_template_name(self):
        data = {'color__black': ['on'], 'type__hoodie': ['on'], 'min_price': ['0'], 'max_price': [self.max_price]}
        response = self.client.post('/catalog/collections', data=data)
        involved_templates = ['online_store/catalog.html', 'online_store/catalog_base.html', 'online_store/base.html',
                              'online_store/header.html', 'online_store/filters_for_all_collections.html',
                              'online_store/collection row.html', 'online_store/collection row.html',
                              'online_store/collections.html']

        self.assertCountEqual([template.name for template in response.templates], involved_templates)
        self.assertTemplateUsed(response, 'online_store/collections.html')

    def test_filter_sort_by_popular(self):
        data = {'sort_by__popular': ['on'], 'min_price': ['0'], 'max_price': [self.max_price]}
        response = self.client.post('/catalog/collections', data=data)
        self.assertEqual(response.status_code, 200)

        products_sort_by_popular = list(Product.objects.order_by('-views', '-pk'))
        catalog = self.get_catalog_by_page(1, products_sort_by_popular)
        self.assertCountEqual(response.context['catalog'], catalog)

        number_pages = self.get_number_pages_by_sorted_products(products_sort_by_popular)
        self.assertEqual(self.get_number_all_pages(response), str(number_pages))

        data = {'act_filters': ["['csrfmiddlewaretoken', 'sort_by__popular']"],
                'filters': ["{'type': [], 'sort_by': ['popular'], 'collection': [], 'size': [], 'color': []}"],
                'min_price': ['0'], 'max_price': [self.max_price], 'page': ['2']}
        self.delete_all_fields_from_cache_directory()
        second_page_response = self.client.post('/catalog/collections', data=data)
        self.assertEqual(self.client.post('/catalog/collections', data=data).status_code, 200)

        catalog = self.get_catalog_by_page(2, products_sort_by_popular)
        self.assertEqual(second_page_response.context['catalog'], catalog)

        self.assertEqual(self.get_page_number(second_page_response), str(2))

    def test_filter_sort_by_recent(self):
        data = {'sort_by__recent': ['on'], 'min_price': ['0'], 'max_price': [self.max_price]}
        response = self.client.post('/catalog/collections', data=data)
        self.assertEqual(response.status_code, 200)

        products_sort_by_recent = list(Product.objects.order_by('-pk'))
        catalog = self.get_catalog_by_page(1, products_sort_by_recent)
        self.assertEqual(response.context['catalog'], catalog)

        number_pages = self.get_number_pages_by_sorted_products(products_sort_by_recent)
        self.assertEqual(self.get_number_all_pages(response), str(number_pages))

        data = {'act_filters': ["['csrfmiddlewaretoken', 'sort_by__recent']"],
                'filters': ["{'type': [], 'sort_by': ['recent'], 'collection': [], 'size': [], 'color': []}"],
                'min_price': ['0'], 'max_price': [self.max_price], 'page': ['2']}
        self.delete_all_fields_from_cache_directory()
        second_page_response = self.client.post('/catalog/collections', data=data)

        self.assertEqual(second_page_response.status_code, 200)

        catalog = self.get_catalog_by_page(2, products_sort_by_recent)
        self.assertEqual(second_page_response.context['catalog'], catalog)

        self.assertEqual(self.get_page_number(second_page_response), str(2))

    def test_filter_sort_by_filling_price(self):
        # self.sort_by_tests(sort_by_filter='filling_price', order_by='-price')
        data = {'sort_by__filling_price': ['on'], 'min_price': ['0'], 'max_price': [self.max_price]}
        response = self.client.post('/catalog/collections', data=data)
        self.assertEqual(response.status_code, 200)

        products_sort_by_filling_price = list(Product.objects.order_by('-price', '-pk'))
        catalog = self.get_catalog_by_page(1, products_sort_by_filling_price)
        self.assertCountEqual(response.context['catalog'], catalog)

        number_pages = self.get_number_pages_by_sorted_products(products_sort_by_filling_price)
        self.assertEqual(self.get_number_all_pages(response), str(number_pages))

        data = {'act_filters': ["['csrfmiddlewaretoken', 'sort_by__filling_price']"],
                'filters': ["{'type': [], 'sort_by': ['filling_price'], 'collection': [], 'size': [], 'color': []}"],
                'min_price': ['0'], 'max_price': [self.max_price], 'page': ['2']}
        self.delete_all_fields_from_cache_directory()
        second_page_response = self.client.post('/catalog/collections', data=data)
        self.assertEqual(second_page_response.status_code, 200)

        catalog = self.get_catalog_by_page(2, products_sort_by_filling_price)
        self.assertEqual(second_page_response.context['catalog'], catalog)

        self.assertEqual(self.get_page_number(second_page_response), str(2))

    def test_filter_sort_by_increasing_price(self):
        data = {'sort_by__increasing_price': ['on'], 'min_price': ['0'], 'max_price': [self.max_price]}
        response = self.client.post('/catalog/collections', data=data)

        self.assertEqual(response.status_code, 200)

        products_sort_by_increasing_price = list(Product.objects.order_by('price', '-pk'))

        catalog = self.get_catalog_by_page(1, products_sort_by_increasing_price)
        self.assertCountEqual(response.context['catalog'], catalog)

        number_pages = self.get_number_pages_by_sorted_products(products_sort_by_increasing_price)
        self.assertEqual(self.get_number_all_pages(response), str(number_pages))

        data = {'act_filters': ["['csrfmiddlewaretoken', 'sort_by__increasing_price']"],
                'filters': ["{'type': [], 'sort_by': ['increasing_price'], 'collection': [], 'size': [], 'color': []}"],
                'min_price': ['0'], 'max_price': [self.max_price], 'page': ['2']}
        self.delete_all_fields_from_cache_directory()
        second_page_response = self.client.post('/catalog/collections', data=data)
        self.assertEqual(second_page_response.status_code, 200)

        catalog = self.get_catalog_by_page(2, products_sort_by_increasing_price)
        self.assertEqual(second_page_response.context['catalog'], catalog)

        self.assertEqual(self.get_page_number(second_page_response), str(2))

    def test_filter_by_t_shirt_type(self):
        data = {'type__t-shirt': ['on'], 'min_price': ['0'], 'max_price': [self.max_price]}
        response = self.client.post('/catalog/collections', data=data)

        t_shirt_type_products = list(Product.objects.filter(type__type__icontains='t-shirt').order_by('-pk'))

        catalog = self.get_catalog_by_page(1, t_shirt_type_products)
        self.assertEqual(response.context['catalog'], catalog)

        number_pages = self.get_number_pages_by_sorted_products(t_shirt_type_products)
        self.assertEqual(self.get_number_all_pages(response), str(number_pages))

        data = {'csrfmiddlewaretoken': ['H9mTA5Naxy4nsDsyVuJfhCLDda9ZlsYKAcMUZP0cx17L1t0Zb7KPZGXJSp3SoLAw'],
                'filters': ["{'type': ['t-shirt'], 'sort_by': [], 'collection': [], 'size': [], 'color': []}"],
                'act_filters': ["['type__t-shirt']"], 'page': ['2'], 'min_price': ['0'], 'max_price': [self.max_price]}
        self.delete_all_fields_from_cache_directory()
        second_page_response = self.client.post('/catalog/collections', data=data)
        self.assertEqual(second_page_response.status_code, 200)

        catalog = self.get_catalog_by_page(2, t_shirt_type_products)
        self.assertEqual(second_page_response.context['catalog'], catalog)

        self.assertEqual(self.get_page_number(second_page_response), str(2))

    def test_filter_by_hoodie_type(self):
        data = {'type__hoodie': ['on'], 'min_price': ['0'], 'max_price': [self.max_price]}
        response = self.client.post('/catalog/collections', data=data)

        hoodie_type_products = list(Product.objects.filter(type__type__icontains='hoodie').order_by('-pk'))

        catalog = self.get_catalog_by_page(1, hoodie_type_products)
        self.assertEqual(response.context['catalog'], catalog)

        number_pages = self.get_number_pages_by_sorted_products(hoodie_type_products)
        self.assertEqual(self.get_number_all_pages(response), str(number_pages))

        data = {'csrfmiddlewaretoken': ['H9mTA5Naxy4nsDsyVuJfhCLDda9ZlsYKAcMUZP0cx17L1t0Zb7KPZGXJSp3SoLAw'],
                'filters': ["{'type': ['hoodie'], 'sort_by': [], 'collection': [], 'size': [], 'color': []}"],
                'act_filters': ["['type__hoodie']"], 'page': ['2'], 'min_price': ['0'], 'max_price': [self.max_price]}
        self.delete_all_fields_from_cache_directory()
        second_page_response = self.client.post('/catalog/collections', data=data)
        if int(self.get_page_number(second_page_response)) > 1:
            self.assertEqual(second_page_response.status_code, 200)

            catalog = self.get_catalog_by_page(2, hoodie_type_products)
            self.assertEqual(response.context['catalog'], catalog)

            self.assertEqual(self.get_page_number(second_page_response), str(2))

    def test_filter_by_sweatshirt_type(self):
        data = {'type__sweatshirt': ['on'], 'min_price': ['0'], 'max_price': [str(self.max_price)]}
        response = self.client.post('/catalog/collections', data=data)

        sweatshirt_type_products = list(Product.objects.filter(type__type__icontains='sweatshirt').order_by('-pk'))

        catalog = self.get_catalog_by_page(1, sweatshirt_type_products)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['catalog'][0]), catalog[0])

        number_pages = self.get_number_pages_by_sorted_products(sweatshirt_type_products)
        self.assertEqual(self.get_number_all_pages(response), str(number_pages))

        data = {'csrfmiddlewaretoken': ['H9mTA5Naxy4nsDsyVuJfhCLDda9ZlsYKAcMUZP0cx17L1t0Zb7KPZGXJSp3SoLAw'],
                'filters': ["{'type': ['sweatshirt'], 'sort_by': [], 'collection': [], 'size': [], 'color': []}"],
                'act_filters': ["['type__sweatshirt']"], 'page': ['2'], 'min_price': ['0'],
                'max_price': [self.max_price]}
        self.delete_all_fields_from_cache_directory()
        second_page_response = self.client.post('/catalog/collections', data=data)
        if int(self.get_page_number(second_page_response)) > 1:
            self.assertEqual(second_page_response.status_code, 200)

            catalog = self.get_catalog_by_page(2, sweatshirt_type_products)
            self.assertEqual(response.context['catalog'], catalog)

            self.assertEqual(self.get_page_number(second_page_response), str(2))

    def test_filter_by_collections(self):
        data = {'collection__yellow art': ['on'], 'collection__red&black': ['on'], 'min_price': ['0'],
                'max_price': [self.max_price]}
        response = self.client.post(reverse('collections'), data=data)

        self.assertEqual(response.status_code, 200)

        catalog = self.get_catalog_by_page(1, list(Product.objects.filter(
                                                    collection__name__in=['yellow art', 'red&black']).order_by('-pk')
                                                   ))
        self.assertEqual(response.context['catalog'], catalog)

    def test_filter_by_price(self):
        data = {'min_price': ['0'], 'max_price': ['40.22']}
        response = self.client.post(reverse('collections'), data=data)
        self.assertEqual(response.status_code, 200)

        products_filtered_by_price = list(Product.objects.filter(price__lte=40.22).order_by('-pk'))
        self.assertEqual(response.context['catalog'], self.get_catalog_by_page(1, products_filtered_by_price))

        data = {'min_price': ['0'], 'max_price': [self.max_price]}
        self.delete_all_fields_from_cache_directory()
        response = self.client.post(reverse('collections'), data=data)
        self.assertEqual(response.status_code, 302)

        data = {'min_price': ['25'], 'max_price': ['20.22']}
        self.delete_all_fields_from_cache_directory()
        response = self.client.post(reverse('collections'), data=data)
        self.assertEqual(response.status_code, 302)

        data = {'min_price': ['40'], 'max_price': [self.max_price]}
        self.delete_all_fields_from_cache_directory()
        response = self.client.post(reverse('collections'), data=data)
        self.assertEqual(response.status_code, 200)

        products_filtered_by_price = list(Product.objects.filter(price__gte=40).order_by('-pk'))
        self.assertEqual(response.context['catalog'], self.get_catalog_by_page(1, products_filtered_by_price))

    def test_color_filter(self):
        data = {'color__black': ['on'], 'min_price': ['0'], 'max_price': [self.max_price]}
        response = self.client.post('/catalog/collections', data=data)

        black_color_products = list(Product.objects.filter(color__icontains='black').order_by('-pk'))

        catalog = self.get_catalog_by_page(1, black_color_products)
        self.assertEqual(response.context['catalog'], catalog)

        number_pages = self.get_number_pages_by_sorted_products(black_color_products)
        self.assertEqual(self.get_number_all_pages(response), str(number_pages))

        data = {'csrfmiddlewaretoken': ['H9mTA5Naxy4nsDsyVuJfhCLDda9ZlsYKAcMUZP0cx17L1t0Zb7KPZGXJSp3SoLAw'],
                'filters': ["{'type': [], 'sort_by': [], 'collection': [], 'size': [], 'color': ['black']}"],
                'act_filters': ["['color__black']"], 'page': ['2'], 'min_price': ['0'], 'max_price': [self.max_price]}
        self.delete_all_fields_from_cache_directory()
        second_page_response = self.client.post('/catalog/collections', data=data)
        self.assertEqual(second_page_response.status_code, 200)

        catalog = self.get_catalog_by_page(2, black_color_products)
        self.assertEqual(second_page_response.context['catalog'], catalog)

        self.assertEqual(self.get_page_number(second_page_response), str(2))

    def test_size_filter(self):
        data = {'size__M': ['on'], 'min_price': ['0'], 'max_price': [self.max_price]}
        response = self.client.post('/catalog/collections', data=data)

        Q_ = get_Q_for_collections_page(self.max_price, 0, {'type': [], 'sort_by': [], 'collection': [],
                                                            'size': ['S'], 'color': []})
        s_size_products = list(Product.objects.filter(Q_).order_by('-pk'))

        catalog = self.get_catalog_by_page(1, s_size_products)
        self.assertEqual(response.context['catalog'], catalog)

        number_pages = self.get_number_pages_by_sorted_products(s_size_products)
        self.assertEqual(self.get_number_all_pages(response), str(number_pages))

        data = {'csrfmiddlewaretoken': ['H9mTA5Naxy4nsDsyVuJfhCLDda9ZlsYKAcMUZP0cx17L1t0Zb7KPZGXJSp3SoLAw'],
                'filters': ["{'type': [], 'sort_by': [], 'collection': [], 'size': ['S'], 'color': []}"],
                'act_filters': ["['size__S']"], 'page': ['2'], 'min_price': ['0'], 'max_price': [self.max_price]}
        self.delete_all_fields_from_cache_directory()
        second_page_response = self.client.post('/catalog/collections', data=data)
        self.assertEqual(second_page_response.status_code, 200)

        catalog = self.get_catalog_by_page(2, s_size_products)
        self.assertEqual(second_page_response.context['catalog'], catalog)

        self.assertEqual(self.get_page_number(second_page_response), str(2))


class RestoreBasketDataByEmailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        list_colors = ['white', 'black']
        Collection.objects.create(name=f'test collection 1',
                                  description='test_collection_description',
                                  views=1)
        TypeClothing.objects.create(type=f'test_type_1', description='test_type_description',
                                    characteristics='test_characteristics', colors='black, white',
                                    delivery='7 - 14 day', size='S, M, XL',
                                    slug=f'test-type-slug-1',
                                    views=1)
        for number in range(1, 4):
            Product.objects.create(collection=Collection.objects.last(), name=f'product {number}',
                                   type=TypeClothing.objects.last(), price=20 + number,
                                   color=choice(list_colors), description_print='description_print_test',
                                   views=20 + number)
        for pk in range(1, 6):
            order_form = OrderForm.objects.create(full_name=f'full_name_{pk}', first_address=f'first_address_{pk}',
                                                  second_address=f'second_address_{pk}', country=f'country_{pk}',
                                                  postal_or_zip_code=f'postal_or_zip_code_{pk}', city=f'city_{pk}',
                                                  company=f'company_{pk}', phone=f'+{pk}0345223541',
                                                  email=f'email{pk}@gmail.com', state='state_{pk}')
            order_form.save()
            for item in range(1, random.randint(1, 5)):
                orders = Orders.objects.create(order_number=order_form,
                                               product=choice(Product.objects.all()),
                                               color=choice(list_colors),
                                               size=choice(['S', 'M', 'L', 'XL']),
                                               quantity=random.randint(1, 5))

    def test_send_email(self):
        response = self.client.post('/basket/restore_data', data={'email': 'email5@gmail.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/basket')

        response = self.client.post(reverse('get_email_for_restore_basket_data'), data={'email': 'email5@gmail.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/basket')

    def test_restore_basket_data(self):
        pk_ = 5
        order_form = OrderForm.objects.create(full_name=f'full_name_{pk_}', first_address=f'first_address_{pk_}',
                                              second_address=f'second_address_{pk_}', country=f'country_{pk_}',
                                              postal_or_zip_code=f'postal_or_zip_code_{pk_}', city=f'city_{pk_}',
                                              company=f'company_{pk_}', phone=f'+{pk_}0345223541',
                                              email=f'email{pk_}@gmail.com', state='state_{pk}')
        response = self.client.get(f'/basket/{urlsafe_base64_encode(force_bytes(order_form.pk))}/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/basket')
        value_result_restore = literal_eval(response.cookies.pop('list_id_orders').value)
        all_order_forms_with_this_email = list(OrderForm.objects.filter(email='email5@gmail.com'
                                                                        ).values_list('pk', flat=True))
        self.assertEqual(value_result_restore, all_order_forms_with_this_email)


class CheapSh0peBasketTest(TestCase):
    fixtures = ['test_db.json', ]

    def test_url(self):
        response = self.client.get('/basket')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('basket'))
        self.assertEqual(response.status_code, 200)

    def test_templates(self):
        response = self.client.get('/basket')
        self.assertTemplateUsed(response, 'online_store/basket.html')

    def test_basket_context(self):
        basket_for_cookies = {}
        basket_products = []
        numbers_orders = []
        for pk in range(1, 6):
            order_form = OrderForm.objects.create(full_name=f'full_name_{pk}', first_address=f'first_address_{pk}',
                                                  second_address=f'second_address_{pk}', country=f'country_{pk}',
                                                  postal_or_zip_code=f'postal_or_zip_code_{pk}', city=f'city_{pk}',
                                                  company=f'company_{pk}', phone=f'+{pk}0345223541',
                                                  email=f'email@gmail.com', state='state_{pk}')
            Orders.objects.create(order_number=order_form,
                                  product=choice(Product.objects.all()),
                                  color=choice(['white', 'black']),
                                  size=choice(['S', 'M', 'L', 'XL']),
                                  quantity=random.randint(1, 5))
            numbers_orders.append(order_form.pk)

        for number in range(1, 5):
            product = choice(Product.objects.filter(pk__in=[1, 2, 3]))
            product_for_basket = {'product_id': product.pk, 'add_color': choice(product.get_color_list()),
                                  'add_size': choice(product.get_size_list())}

            len_basket_for_cookies = len(basket_for_cookies)
            quantity_products_with_same_id_bun_with_different_other_characteristic = len(basket_for_cookies.pop(
                                                                                         product.pk, []))
            q_p_w_s_i_b_w_d_o_c = quantity_products_with_same_id_bun_with_different_other_characteristic

            basket_for_cookies = add_product_in_basket_or_update_data(basket_for_cookies, product_for_basket)
            if len(basket_for_cookies) > len_basket_for_cookies or \
                    len(basket_for_cookies[product.pk]) > q_p_w_s_i_b_w_d_o_c:
                basket_products.append(product)

        self.client.cookies.load({'basket': json.dumps(basket_for_cookies),
                                  'list_id_orders': json.dumps(numbers_orders)})

        response = self.client.get('/basket')
        self.assertCountEqual(response.context['basket'], basket_products)
        self.assertCountEqual(response.context['country_numbers'], PhoneBlank.objects.all())
        self.assertEqual(response.context['css'], 'basket.css')
        self.assertIsInstance(response.context['form_for_restore_basket_data'].__dict__['fields']['email'],
                              SendEmailForm.base_fields['email'].__class__)

        self.assertEqual(list(response.context['list_orders'].keys()),
                         [str(number_order) for number_order in numbers_orders])

    def test_post_method(self):
        pk = 1
        basket_for_cookies = {}
        order_form = OrderForm.objects.create(full_name=f'full_name_{pk}', first_address=f'first_address_{pk}',
                                              second_address=f'second_address_{pk}', country=f'country_{pk}',
                                              postal_or_zip_code=f'postal_or_zip_code_{pk}', city=f'city_{pk}',
                                              company=f'company_{pk}', phone=f'+{pk}0345223541',
                                              email=f'email@gmail.com', state=f'state_{pk}')
        for number in range(1, 6):
            product = choice(Product.objects.filter(pk__in=[1, 2, 3]))
            product_for_basket = {'product_id': product.pk, 'add_color': choice(product.get_color_list()),
                                  'add_size': choice(product.get_size_list())}
            basket_for_cookies = add_product_in_basket_or_update_data(basket_for_cookies, product_for_basket)

        number_formset = 0
        orders = {}
        orders_TOTAL_FORMS = 0
        for key, value in basket_for_cookies.items():
            if len(value) > 1:
                for product in value:
                    orders.update({f'orders-{number_formset}-product': key,
                                   f'orders-{number_formset}-color': product['color'],
                                   f'orders-{number_formset}-size': product['size'],
                                   f'orders-{number_formset}-quantity': product['quantity']})
                    number_formset += 1
                    orders_TOTAL_FORMS += 1
            else:
                orders.update({f'orders-{number_formset}-product': key,
                               f'orders-{number_formset}-color': value[0]['color'],
                               f'orders-{number_formset}-size': value[0]['size'],
                               f'orders-{number_formset}-quantity': value[0]['quantity']})
                number_formset += 1
                orders_TOTAL_FORMS += 1
        data = {'order_form-email': order_form.email, 'order_form-phone': [order_form.phone],
                'order_form-full_name': [order_form.full_name], 'order_form-first_address': [order_form.first_address],
                'order_form-second_address': [order_form.second_address], 'order_form-country': [order_form.country],
                'order_form-postal_or_zip_code': [order_form.postal_or_zip_code], 'order_form-city': [order_form.city],
                'order_form-company': [order_form.company], 'orders-INITIAL_FORMS': 0}
        data.update(orders)
        data['orders-TOTAL_FORMS'] = orders_TOTAL_FORMS

        len_orders_forms = OrderForm.objects.all().count()
        len_orders = Orders.objects.all().count()

        response = self.client.post('/basket', data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/basket')
        self.assertEqual(len_orders_forms + 1, OrderForm.objects.all().count())
        self.assertEqual(len_orders + orders_TOTAL_FORMS, Orders.objects.all().count())
        client_order_form = OrderForm.objects.order_by('-date_create')[0].pk
        self.assertEqual(client_order_form, literal_eval(self.client.cookies.pop('list_id_orders').value)[0])
