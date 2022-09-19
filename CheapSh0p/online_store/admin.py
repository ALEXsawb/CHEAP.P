from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_collection', 'name', 'get_type', 'price', 'get_html_photo', 'views', 'color',
                    'is_published', 'description_print', 'slug')
    list_display_links = ('id', 'get_collection', 'name', 'get_type')
    search_fields = ('id', 'name', 'collection__name', 'type__type', 'price', 'color', 'slug')
    list_editable = ('description_print', 'color', 'is_published')
    prepopulated_fields = {"slug": ('name', )}
    fields = ('name', 'collection', 'type', 'price', 'color', 'photo', 'get_html_photo', 'is_published',
              'description_print', 'slug', 'views', 'time_update', 'time_create')
    readonly_fields = ('time_update', 'time_create', 'views', 'get_html_photo')

    def get_collection(self, obj):
        url = reverse('admin:%s_%s_changelist' % ('online_store', 'collection')) + f'?q={obj.collection.pk}'
        return mark_safe(u'<a href="%s">%s</a>' % (url, obj.collection.name))

    def get_type(self, obj):
        url = reverse('admin:%s_%s_changelist' % ('online_store', 'typeclothing')) + f'?q={obj.type.pk}'
        return mark_safe(u'<a href="%s">%s</a>' % (url, obj.type.type))

    def get_html_photo(self, obj):
        if obj.photo:
            return mark_safe(f'<image src="{obj.photo.url}" width=150px>')

    get_html_photo.short_description = 'Изображение товара'
    get_collection.short_description = 'Колекция'
    get_type.short_description = 'Просмотры'


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'description', 'is_published', 'views')
    list_display_links = ('id', 'name')
    list_editable = ('is_published', )
    search_fields = ('id', 'name')
    prepopulated_fields = {"slug": ('name',)}
    readonly_fields = ('views', )


class TypeClothingAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'slug', 'colors', 'size', 'characteristics', 'description', 'delivery',
                    'views')
    list_display_links = ('id', 'type')
    search_fields = ('id', 'type', 'slug', 'colors', 'size')
    prepopulated_fields = {'slug': ('type', )}


class DeliveryFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'first_address', 'second_address', 'country', 'postal_or_zip_code', 'city',
                    'company', 'phone', 'email', 'state', 'date_create')
    search_fields = ('id', 'email', 'full_name', 'phone', 'date_create')
    readonly_fields = ('date_create', )


class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_order_number', 'get_product', 'color', 'size', 'quantity', 'order_in_processing')
    list_display_links = ('get_product', 'get_order_number')
    search_fields = ('id', 'size', 'color', 'product__name', 'order_number__pk', 'product__collection__name')

    def get_order_number(self, obj):
        return str(obj.order_number.id)

    def get_order_number(self, obj):
        url = reverse('admin:%s_%s_change' % ('online_store', 'orderform'), args=[obj.order_number.pk])
        return mark_safe(u'<a href="%s">%s</a>' % (url, obj.order_number.pk))

    def get_product(self, obj):
        url = reverse('admin:%s_%s_changelist' % ('online_store', 'product')) + f'?q={obj.product.slug}'
        return mark_safe(u'<a href="%s">%s</a>' % (url, f'{obj.product.collection} | {obj.product.name}'))

    get_order_number.short_description = 'Номер заказа'
    get_product.short_description = 'Товар'


admin.site.register(Product, ProductAdmin, )
admin.site.register(Collection, CollectionAdmin)
admin.site.register(OrderForm, DeliveryFormAdmin)
admin.site.register(TypeClothing, TypeClothingAdmin)
admin.site.register(Orders, OrdersAdmin)
