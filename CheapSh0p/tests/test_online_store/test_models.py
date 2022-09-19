from django.test import TestCase
from online_store.models import Product, Collection, TypeClothing, PhoneBlank, OrderForm, Orders


class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Запускается перед тестом,обычно задаються данные, которые понадобяться при работе теста в целом"""
        Collection.objects.create(name='test collection', description='test_collection_description',
                                  views=0)
        TypeClothing.objects.create(type='test_type', description='test_type_description',
                                    characteristics='test_characteristics', colors='black, white',
                                    delivery='7 - 14 day', size='S, M, XL', slug='test-type-slug',
                                    views=0)

    def setUp(self) -> None:
        """Запускается перед каждым методом теста, тоесть грубоговоря перед каждым тестом"""
        self.product = Product.objects.create(collection=Collection.objects.last(), name='product 1',
                                              type=TypeClothing.objects.last(), price='55.33', color='white, black',
                                              description_print='description_print_test',
                                              views=100)

    def test_verbose_name_all_fields_product(self):
        fields_dict = {'collection': 'Коллекция',
                       'name': 'Название принтов',
                       'type': 'Тип одежды',
                       'photo': 'Фото',
                       'color': 'Цвет',
                       'description_print': 'Описание принта',
                       'time_create': 'Время создания',
                       'time_update': 'Время изминения',
                       'is_published': 'Публикация',
                       'slug': 'URL',
                       'views': 'Просмотры'}
        for field_name in fields_dict:
            self.assertEquals(self.product._meta.get_field(field_name).verbose_name, fields_dict[field_name])
        self.assertEquals(self.product._meta.verbose_name, 'Товар')
        self.assertEquals(self.product._meta.verbose_name_plural, 'Товары')

    def test_max_length_field_product(self):
        self.assertEquals(self.product._meta.get_field('name').max_length, 100)
        self.assertEquals(self.product._meta.get_field('color').max_length, 50)
        self.assertEquals(self.product._meta.get_field('slug').max_length, 55)
        self.assertEquals(self.product._meta.get_field('price').max_digits, 7)

    def test__str__(self):
        self.assertEquals(str(self.product), 'test_type   |   test collection   |   product 1')

    def test_get_absolute_url(self):
        self.assertEquals(self.product.get_absolute_url(), '/catalog/test-collection/product-1')

    def test_get_color_list(self):
        self.assertEquals(self.product.get_color_list(), ['white', 'black'])

    def test_get_size_list(self):
        self.assertEquals(self.product.get_size_list(), ["S", "M", "XL"])

    def test_save_method(self):
        product = Product.objects.create(collection=Collection.objects.last(), name='product 2',
                                         type=TypeClothing.objects.last(), price='55.33', color='white',
                                         description_print='description_print_test',
                                         views=100)
        product.save()
        self.assertEqual(product, Product.objects.last())


class CollectionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        TypeClothing.objects.create(type='test_type', description='test_type_description',
                                    characteristics='test_characteristics', colors='black, white',
                                    delivery='7 - 14 day', size='S,M,XL', slug='test-type-slug',
                                    views=0)

    def setUp(self) -> None:
        self.collection = Collection.objects.create(name='test collection', description='test_collection_description',
                                                    views=0)

        self.product = Product.objects.create(collection=Collection.objects.last(), name='product 1',
                                              type=TypeClothing.objects.last(), price='55.33', color='white',
                                              description_print='description_print_test',
                                              views=100)

    def test_verbose_name_all_fields_collection(self):
        verbose_name_dict = {'name': "Название",
                             'description': "Описание",
                             'slug': "URL",
                             'is_published': "Публикация",
                             'views': "Просмотры"}
        for field_name in verbose_name_dict:
            self.assertEquals(self.collection._meta.get_field(field_name).verbose_name, verbose_name_dict[field_name])
        self.assertEquals(self.collection._meta.verbose_name, "Колекции")
        self.assertEquals(self.collection._meta.verbose_name_plural, "Колекции")

    def test__str__(self):
        self.assertEquals(str(self.collection), 'test collection')

    def test_get_absolute_url(self):
        self.assertEquals(self.collection.get_absolute_url(), '/catalog/test-collection')

    def test_products_this_collection(self):
        self.assertEquals(list(self.collection.get_products_this_collection()), [self.product, ])
        product_2 = Product.objects.create(collection=Collection.objects.last(), name='product 2',
                                           type=TypeClothing.objects.last(), price='55.54', color='white',
                                           description_print='description_print_test_2',
                                           views=100)

        product_3 = Product.objects.create(collection=Collection.objects.last(), name='product 3',
                                           type=TypeClothing.objects.last(), price='5.33', color='black',
                                           description_print='description_print_test_3',
                                           views=100)
        self.assertEquals(list(self.collection.get_products_this_collection()),
                          [self.product, product_2, product_3])

    def test_length_fields(self):
        self.assertEquals(self.collection._meta.get_field('name').max_length, 100)
        self.assertEquals(self.collection._meta.get_field('slug').max_length, 55)


class TypeClothingModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Запускается перед тестом,обычно задаються данные, которые понадобяться при работе теста в целом"""
        Collection.objects.create(name='test collection', description='test_collection_description',
                                  views=0)

    def setUp(self) -> None:
        """Запускается перед каждым методом теста, тоесть грубоговоря перед каждым тестом"""
        self.type_clothing = TypeClothing.objects.create(type='test_type', description='test_type_description',
                                                         characteristics='test_characteristics', colors='black, white',
                                                         delivery='7 - 14 day', size='S, M, XL', slug='test-type-slug',
                                                         views=0)

        self.product_1 = Product.objects.create(collection=Collection.objects.last(), name='product 1',
                                                type=TypeClothing.objects.last(), price='55.33', color='white',
                                                description_print='description_print_test',
                                                views=110)
        self.product_2 = Product.objects.create(collection=Collection.objects.last(), name='product 2',
                                                type=TypeClothing.objects.last(), price='55.54', color='white',
                                                description_print='description_print_test_2',
                                                views=120)
        self.product_3 = Product.objects.create(collection=Collection.objects.last(), name='product 3',
                                                type=TypeClothing.objects.last(), price='5.33', color='black',
                                                description_print='description_print_test_3',
                                                views=130)

    def test_verbose_name_all_fields_type_clothing(self):
        verbose_name_dict = {'type': "Тип одежды",
                             'description': "Описание",
                             'characteristics': "Характеристики",
                             'colors': "Цвета",
                             'delivery': "Доставка",
                             'size': "Размеры",
                             'slug': "URL",
                             'views': "Просмотры"}
        for field_name in verbose_name_dict:
            self.assertEquals(self.type_clothing._meta.get_field(field_name).verbose_name,
                              verbose_name_dict[field_name])
        self.assertEquals(self.type_clothing._meta.verbose_name, "Тип одежды")
        self.assertEquals(self.type_clothing._meta.verbose_name_plural, "Типы одежды")

    def test_get_absolute_url(self):
        self.assertEquals(self.type_clothing.get_absolute_url(), '/api/v1/type/test_type')

    def test_get_products_this_type(self):
        self.assertEquals(list(self.type_clothing.get_products_this_type()),
                          [self.product_1, self.product_2, self.product_3])

    def test_get_size_list(self):
        self.assertEquals(self.type_clothing.get_size_list(), ["S", "M", "XL"])

    def test_get_color_list(self):
        self.assertEquals(list(self.type_clothing.get_color_list()), ['black', 'white'])

    def test_length_fields(self):
        self.assertEquals(self.type_clothing._meta.get_field('type').max_length, 50)
        self.assertEquals(self.type_clothing._meta.get_field('slug').max_length, 55)
        self.assertEquals(self.type_clothing._meta.get_field('size').max_length, 8)
        self.assertEquals(self.type_clothing._meta.get_field('delivery').max_length, 100)
        self.assertEquals(self.type_clothing._meta.get_field('colors').max_length, 100)

    def test_update_colors(self):
        self.type_clothing.colors = 'black'
        self.type_clothing.save()
        for product in self.type_clothing.product_set.all():
            if product.color not in self.type_clothing.get_color_list():
                self.assertFalse(product.is_published)


class PhoneBlankTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.phone_blank = PhoneBlank.objects.create(region_number='+380', country='Ukraine')

    def test_verbose_name_all_fields_phone_blank(self):
        fields_dict = {'region_number': 'Региональный номер телефона',
                       'country': 'Страна'}
        for field_name in fields_dict:
            self.assertEquals(self.phone_blank._meta.get_field(field_name).verbose_name, fields_dict[field_name])
        self.assertEquals(self.phone_blank._meta.verbose_name, 'Региональные номера')
        self.assertEquals(self.phone_blank._meta.verbose_name_plural, 'Региональные номера')

    def test_max_length_field_product(self):
        self.assertEquals(self.phone_blank._meta.get_field('region_number').max_length, 10)
        self.assertEquals(self.phone_blank._meta.get_field('country').max_length, 30)

    def test__str__(self):
        self.assertEqual(str(self.phone_blank), f'{self.phone_blank.region_number} {self.phone_blank.country}')


class OrdersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        OrderForm.objects.create(full_name='ALex', first_address='first address',
                                 second_address='second address', country='UA',
                                 postal_or_zip_code='50050', city='KR', phone='phone',
                                 email='lapudsh@gmail.com',
                                 company='fdfsfsdf')
        collection = Collection.objects.create(name='test collection', description='test_collection_description',
                                               views=0)
        type_ = TypeClothing.objects.create(type='test_type', description='test_type_description',
                                            characteristics='test_characteristics', colors='black, white',
                                            delivery='7 - 14 day', size='S, M, XL', slug='test-type-slug',
                                            views=0)
        product = Product.objects.create(collection=collection, name='product 1',
                                         type=type_, price='55.33', color='white',
                                         description_print='description_print_test',
                                         views=100)

        cls.order = Orders(order_number=OrderForm.objects.last(), product=product, color='white', size='S', quantity=3)

    def test_verbose_name_all_fields_orders(self):
        fields_dict = {'order_number': 'Номер заказа(заказчика)',
                       'product': 'Продукт заказа',
                       'color': 'Цвет заказа',
                       'size': 'Размер заказа',
                       'quantity': 'Количество заказанного товара',
                       'order_in_processing': 'Заказ в обработке'}
        for field_name in fields_dict:
            self.assertEqual(self.order._meta.get_field(field_name).verbose_name, fields_dict[field_name])
        self.assertEqual(self.order._meta.verbose_name, 'Заказ')
        self.assertEqual(self.order._meta.verbose_name_plural, 'Заказы')

    def test_length_fields(self):
        self.assertEqual(self.order._meta.get_field('color').max_length, 20)
        self.assertEqual(self.order._meta.get_field('size').max_length, 4)

    def test__str__(self):
        self.assertEqual(str(self.order), (f"{self.order.order_number.pk} ----> id:{self.order.pk}, "
                                           f"{self.order.product.pk}, {self.order.color}, "f"{self.order.size}, "
                                           f"{self.order.quantity}, in_processing: {self.order.order_in_processing}"))


class OrderFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.order_form = OrderForm.objects.create(full_name='ALex', first_address='first address',
                                                  second_address='second address', country='UA',
                                                  postal_or_zip_code='50050', city='KR', phone='phone',
                                                  email='shdok@gmail.com',
                                                  company='fdfsfsdf')

    def test_verbose_name_all_fields_order_form(self):
        fields_dict = {'full_name': 'Полное имя',
                       'first_address': 'Первый адресс',
                       'second_address': 'Второй адресс',
                       'country': 'Страна',
                       'postal_or_zip_code': 'Почтовый индекс',
                       'city': 'Город',
                       'company': 'Данные о компании',
                       'phone': 'Номер телефона',
                       'email': 'email',
                       'state': 'Статус заказа',
                       'date_create': 'Время создания'}
        for field_name in fields_dict:
            self.assertEqual(self.order_form._meta.get_field(field_name).verbose_name, fields_dict[field_name])
        self.assertEqual(self.order_form._meta.verbose_name, 'Форма заказа')
        self.assertEqual(self.order_form._meta.verbose_name_plural, 'Формы заказов')

    def test_length_fields(self):
        self.assertEqual(self.order_form._meta.get_field('full_name').max_length, 100)
        self.assertEqual(self.order_form._meta.get_field('first_address').max_length, 150)
        self.assertEqual(self.order_form._meta.get_field('second_address').max_length, 150)
        self.assertEqual(self.order_form._meta.get_field('country').max_length, 100)
        self.assertEqual(self.order_form._meta.get_field('postal_or_zip_code').max_length, 400)
        self.assertEqual(self.order_form._meta.get_field('city').max_length, 100)
        self.assertEqual(self.order_form._meta.get_field('company').max_length, 300)
        self.assertEqual(self.order_form._meta.get_field('phone').max_length, 20)
        self.assertEqual(self.order_form._meta.get_field('state').max_length, 200)
