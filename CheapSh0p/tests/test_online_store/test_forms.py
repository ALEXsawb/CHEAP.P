from typing import Union

from django.forms import TextInput, NumberInput
from django.db.models.aggregates import Max
from django.test import TestCase
from online_store.forms import AddDeliveryForm, AddOrderInBasket, OrderCreationMultiForm, OrderForm
from online_store.models import Product, Collection, TypeClothing, OrderForm as ModelOrderForm, Orders


def get_order_and_order_form():
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
    order_form = ModelOrderForm.objects.create(full_name='ALex', first_address='first address',
                                               second_address='second address', country='UA',
                                               postal_or_zip_code='50050', city='KR', phone='phone',
                                               email='lapu2@gmail.com',
                                               company='fdfsfsdf')
    return AddOrderInBasket({'product': product.pk, 'color': 'white', "size": 'S', "quantity": 3}), order_form


class AddDeliveryFormTest(TestCase):

    def test_all_show_fields(self):
        show_field_list_for_TextInput = ['id', 'full_name', 'first_address', 'second_address', 'country',
                                         'postal_or_zip_code', 'city', 'company', 'email', 'phone']
        self.assertEquals(AddDeliveryForm.Meta.fields, show_field_list_for_TextInput)

    def test_field_list_with_TextInput(self):
        show_field_list_for_TextInput = ['id', 'full_name', 'first_address', 'second_address', 'country',
                                         'postal_or_zip_code', 'city', 'company', 'email', 'phone']
        field_with_new_TextInput_widgets = ['first_address', 'second_address', 'postal_or_zip_code',
                                            'order_number', 'company', 'state']
        for field in field_with_new_TextInput_widgets:
            if field in show_field_list_for_TextInput:
                self.assertTrue(isinstance(AddDeliveryForm().fields[field].widget, TextInput))


class AddOrderInBasketTest(TestCase):

    def test_show_fields(self):
        show_fields = ['product', 'color', 'size', 'quantity']
        self.assertEquals(AddOrderInBasket.Meta.fields, show_fields)

    def test_widgets_form(self):
        self.assertIsInstance(AddOrderInBasket().fields['product'].widget, NumberInput)
        self.assertIsInstance(AddOrderInBasket().fields['color'].widget, TextInput)

    def test_model_form_data_save(self):
        order, order_number = get_order_and_order_form()
        if order.is_valid():
            order.save(order_form_number=order_number)

    def test_method_color_clean(self):
        order, _ = get_order_and_order_form()
        self.assertTrue(order.is_valid())

        order = AddOrderInBasket({'product': order.data['product'], 'color': 'yellow', "size": 'S', "quantity": 3})
        self.assertFalse(order.is_valid())
        self.assertEqual(order._errors['color'][0], 'There is no product( test collection product 1 ) in this color')


class OrderCreationMultiFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Запускается перед тестом,обычно задаються данные, которые понадобяться при работе теста в целом"""
        order, order_form = get_order_and_order_form()
        cls.data = {'order_form-full_name': ['ALex'],
                    'order_form-first_address': ['first address'],
                    'order_form-second_address': ['second address'],
                    'order_form-country': ['UA'],
                    'order_form-postal_or_zip_code': ['50050'],
                    'order_form-city': ['KR'],
                    'order_form-company': ['fdfsfsdf'],
                    'order_form-order_number': ["company"],
                    'order_form-phone': ['phone'],
                    'order_form-email': 'lapdsfu@gmail.com',
                    }

        cls.add_new_order_in_orders(cls.data, order, 0)
        cls.data['orders-TOTAL_FORMS'] = 1
        cls.data['orders-INITIAL_FORMS'] = 0

        cls.form = OrderCreationMultiForm(data=cls.data, quantity_orders=1)
        cls.order = order
        cls.order_form = order_form

    @staticmethod
    def get_template_product(product_id: int, name='product', price='50.00', color='white,black', views=150):
        name += ' ' + str(product_id)
        return Product.objects.create(collection=Collection.objects.last(), name=name, type=TypeClothing.objects.last(),
                                      price=price, color=color, description_print='description_print_test',
                                      views=views)

    @staticmethod
    def add_new_order_in_orders(data, order: AddOrderInBasket, id_order_in_orders: Union[int, str, float]):
        for key in order.data:
            data[f'orders-{id_order_in_orders}-' + key] = order.data[key]
        if 'orders-TOTAL_FORMS' in data:
            data['orders-TOTAL_FORMS'] += 1

    def test_is_valid_method_on_base_form(self):
        self.assertTrue(self.form.is_valid())

    def test_is_valid_and_save_method_in_form_with_several_orders_form(self):
        get_order_and_order_form()
        product_2 = self.get_template_product(2)
        order_2 = AddOrderInBasket({'product': product_2.pk, 'color': 'black', "size": 'M', "quantity": 5})
        self.add_new_order_in_orders(self.data, order_2, 1)

        product_3 = self.get_template_product(3)
        order_3 = AddOrderInBasket({'product': product_3.pk, 'color': 'white', "size": 'S', "quantity": 2})
        self.add_new_order_in_orders(self.data, order_3, 2)

        for key in {'product': 1, 'color': 'black', "size": 'L', "quantity": 10}:
            self.data[f'orders-{3}-' + key] = {'product': 1, 'color': 'black', "size": 'L', "quantity": 10}[key]

        self.assertTrue(self.form.is_valid())
        self.assertEqual(len(self.form.cleaned_data['orders']), 3)

        client_order_number = self.form.save().pk
        self.assertEqual(len(Orders.objects.filter(order_number=client_order_number)), 3)

    def test_save_method_on_base_form(self):
        self.form.is_valid()
        client_order_form_number = self.form.save().pk
        last_order_form = OrderForm.objects.aggregate(Max('pk'))['pk__max']
        self.assertEqual(client_order_form_number, last_order_form)

    def test_is_valid_method_and_save_method_in_form_with_deleted_element(self):
        """Сохранение заказа, что был объявлен при создании класса"""
        self.form.is_valid()
        self.form.save()

        """Формирование второго и третьего заказа на базе первого(расширение данных указанных при объявлении класса - 
           использование атрибутов класса)"""
        product_2 = self.get_template_product(2)
        order_2 = AddOrderInBasket({'product': product_2.pk, 'color': 'black', "size": 'M', "quantity": 5})
        self.add_new_order_in_orders(self.data, order_2, 1)

        product_3 = self.get_template_product(3)
        order_3 = AddOrderInBasket({'product': product_3.pk, 'color': 'black', "size": 'M', "quantity": 5})
        self.add_new_order_in_orders(self.data, order_3, 2)

        """Удаление первого продукта заказа, при оформлении заказа на сайте"""
        self.data['orders-0-DELETE'] = ['on']

        self.form = OrderCreationMultiForm(data=self.data, quantity_orders=2)
        self.assertTrue(self.form.is_valid())

        client_order_form_number = self.form.save().pk
        last_order_form = OrderForm.objects.aggregate(Max('pk'))['pk__max']
        self.assertEqual(client_order_form_number, last_order_form)

        self.assertEqual(len(Orders.objects.filter(order_number=client_order_form_number)), 2)
        self.assertEqual(
            list(Orders.objects.filter(order_number=client_order_form_number).values_list('product__name', flat=True)),
            ['product 2', 'product 3']
        )

        """Проводим проверку с удалением уже 2 элемента(продукта, товара) заказа"""
        self.data['orders-1-DELETE'] = ['on']
        del self.data['orders-0-DELETE']
        self.data['orders-TOTAL_FORMS'] = '3'

        self.form = OrderCreationMultiForm(data=self.data, quantity_orders=2)
        self.assertTrue(self.form.is_valid())

        client_order_form_number = self.form.save().pk
        last_order_form = OrderForm.objects.aggregate(Max('pk'))['pk__max']
        self.assertEqual(client_order_form_number, last_order_form)

        self.assertEqual(len(Orders.objects.filter(order_number=client_order_form_number)), 2)
        self.assertCountEqual(
            list(Orders.objects.filter(order_number=client_order_form_number).values_list('product__name', flat=True)),
            ['product 1', 'product 3']
            )

