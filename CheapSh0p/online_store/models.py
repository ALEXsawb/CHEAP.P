from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from CheapSh0p.settings import STANDARD_SIZES

# https://djbook.ru/rel3.0/topics/db/models.html#relationships


def get_size_list_by_sizes_string(sizes: str) -> list:
    sizes = sizes.replace(' ', '')
    if '-' in sizes:
        return STANDARD_SIZES[STANDARD_SIZES.index(sizes.split('-')[0]):STANDARD_SIZES.index(sizes.split('-')[-1])+1]
    else:
        return sizes.split(',')


def get_color_list_by_colors_string(colors: str) -> list:
    return colors.replace(' ', '').split(',')


class TypeClothing(models.Model):
    type = models.CharField(max_length=50, verbose_name='Тип одежды')
    description = models.TextField(verbose_name='Описание')
    characteristics = models.TextField(verbose_name='Характеристики')
    colors = models.CharField(max_length=100, verbose_name='Цвета')
    delivery = models.CharField(max_length=100, verbose_name='Доставка')
    size = models.CharField(max_length=8, verbose_name='Размеры')
    slug = models.SlugField(max_length=55, verbose_name='URL')
    views = models.PositiveBigIntegerField(default=0, verbose_name='Просмотры')

    class Meta:
        verbose_name = 'Тип одежды'
        verbose_name_plural = "Типы одежды"

    def __str__(self):
        return f"{self.type} {self.colors} {self.size}"

    def get_absolute_url(self):
        return reverse('type-detail', kwargs={'slug': self.slug})

    def get_products_this_type(self):
        return Product.objects.filter(type_id=self.pk)

    def get_size_list(self):
        return get_size_list_by_sizes_string(sizes=self.size)

    def get_color_list(self):
        return get_color_list_by_colors_string(self.colors)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.type)
        products_with_this_type = self.product_set.all()
        type_colors = self.get_color_list()

        if products_with_this_type:
            for product in products_with_this_type:
                product_colors = get_color_list_by_colors_string(product.color)
                for color in product_colors:
                    if color not in type_colors:
                        product_colors.remove(color)
                if product_colors:
                    product.color = ','.join(product_colors)
                    product.is_published = True
                else:
                    product.is_published = False
                product.save()
        super(TypeClothing, self).save(*args, **kwargs)


class Collection(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    is_published = models.BooleanField(default=True, verbose_name='Публикация')
    slug = models.SlugField(max_length=55, verbose_name='URL')
    views = models.PositiveBigIntegerField(default=0, verbose_name='Просмотры')

    class Meta:
        verbose_name = 'Колекции'
        verbose_name_plural = "Колекции"
        ordering = ['name', ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('collection', kwargs={'collection_slug': self.slug})

    def get_products_this_collection(self):
        return self.product_set.all()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        products_this_collection = self.get_products_this_collection()
        if products_this_collection:
            for product in products_this_collection:
                product.is_published = self.is_published
                product.save()
        super(Collection, self).save(*args, **kwargs)


class Product(models.Model):
    collection = models.ForeignKey('Collection', on_delete=models.PROTECT, verbose_name='Коллекция')
    name = models.CharField(max_length=100, verbose_name='Название принтов')
    type = models.ForeignKey('TypeClothing', on_delete=models.PROTECT, verbose_name='Тип одежды')
    price = models.DecimalField(max_digits=7, decimal_places=2)
    photo = models.ImageField(verbose_name='Фото', null=True)
    color = models.CharField(max_length=50, verbose_name='Цвет')
    description_print = models.TextField(verbose_name='Описание принта')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время изминения')
    is_published = models.BooleanField(default=True, verbose_name='Публикация')
    slug = models.SlugField(max_length=55, verbose_name='URL')
    views = models.PositiveBigIntegerField(default=0, verbose_name='Просмотры')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = "Товары"

    def __str__(self):
        return f'{self.type.type}   |   {self.collection.name}   |   {self.name}'

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug, 'collection_slug': self.collection.slug})

    def get_size_list(self):
        return get_size_list_by_sizes_string(sizes=self.type.size)

    def get_color_list(self):
        return get_color_list_by_colors_string(self.color)

    def save(self, *args, **kwargs):
        self.photo.name = f'products/{self.collection.name}/{self.name}.jpg'
        self.slug = slugify(self.name)
        list_available_colors = self.type.get_color_list()
        for color in self.get_color_list():
            if color not in list_available_colors:
                if self.is_published:
                    raise ValidationError(('An unavailable color is listed in the product color list. The colors of the'
                                           ' product must match the colors of the product type.'))
        super().save(*args, **kwargs)


class PhoneBlank(models.Model):
    region_number = models.CharField(max_length=10, verbose_name='Региональный номер телефона')
    country = models.CharField(max_length=30, verbose_name='Страна')

    def __str__(self):
        return f"{self.region_number} {self.country}"

    class Meta:
        verbose_name = 'Региональные номера'
        verbose_name_plural = "Региональные номера"
        ordering = ['country', ]


class Orders(models.Model):
    order_number = models.ForeignKey('OrderForm', on_delete=models.PROTECT, verbose_name='Номер заказа(заказчика)')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name='Продукт заказа')
    color = models.CharField(max_length=20, verbose_name='Цвет заказа')
    size = models.CharField(max_length=4, verbose_name='Размер заказа')
    quantity = models.PositiveSmallIntegerField(verbose_name='Количество заказанного товара')
    order_in_processing = models.BooleanField(default=True, verbose_name='Заказ в обработке')

    def __str__(self):
        try:
            return (f"{self.order_number.pk} ----> id:{self.pk}, {self.product.pk}, {self.color}, {self.size},"
                    f" {self.quantity}, in_processing: {self.order_in_processing}")
        except:
            return (f"id:{self.pk}, {self.product.pk}, {self.color}, {self.size}, {self.quantity},"
                    f" in_processing: {self.order_in_processing}")

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Заказы"
        ordering = ['-order_number', ]


class OrderForm(models.Model):
    full_name = models.CharField(max_length=100, verbose_name='Полное имя')
    first_address = models.TextField(max_length=150, verbose_name='Первый адресс')
    second_address = models.TextField(max_length=150, verbose_name='Второй адресс', null=True)
    country = models.CharField(max_length=100, verbose_name="Страна")
    postal_or_zip_code = models.TextField(max_length=400, verbose_name='Почтовый индекс')
    city = models.CharField(max_length=100, verbose_name='Город')
    company = models.TextField(max_length=300, verbose_name='Данные о компании', null=True)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True)
    email = models.EmailField(verbose_name='email')
    state = models.CharField(max_length=200, verbose_name='Статус заказа', default='waiting for processing')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    class Meta:
        verbose_name = 'Форма заказа'
        verbose_name_plural = "Формы заказов"
        ordering = ['-date_create', ]
