from django import forms
from django.forms import formset_factory
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from betterforms.multiform import MultiModelForm
from .models import OrderForm, Orders


def set_input_text_wherever_needed(list_name_this_fields, widgets=False):
    if not widgets:
        widgets = {}
    for field in list_name_this_fields:
        widgets[field] = forms.TextInput()
    return widgets


class AddDeliveryForm(forms.ModelForm):
    class Meta:
        model = OrderForm
        fields = ['id', 'full_name', 'first_address', 'second_address', 'country', 'postal_or_zip_code', 'city',
                  'company', 'email', 'phone']
        widgets = set_input_text_wherever_needed(['first_address', 'second_address', 'postal_or_zip_code',
                                                  'order_number', 'company', 'state'])


class AddOrderInBasket(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['product', 'color', 'size', 'quantity']
        widgets = {
            'product': forms.NumberInput(),
            'color': forms.TextInput(),
        }

    def clean_color(self):
        data = self.cleaned_data['color']
        product = self.cleaned_data['product']

        if data not in product.color:
            raise ValidationError(_(f'There is no product( {product.collection.name} {product.name} ) in this color'))
        return data

    def save(self, commit=True, **kwargs):
        order_form_number = kwargs.pop('order_form_number')
        if not self.cleaned_data.pop('DELETE', None):
            self.cleaned_data['order_number'] = order_form_number
            Orders(**self.clean()).save()


class SendEmailForm(forms.ModelForm):
    email = forms.EmailField(label=_("Email"), max_length=200, widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

    class Meta:
        model = OrderForm
        fields = ('email', )


class OrderCreationMultiForm(MultiModelForm):
    form_classes = {'order_form': AddDeliveryForm, 'orders': AddOrderInBasket}

    def __init__(self, *args, **kwargs):
        if 'quantity_orders' not in kwargs:
            raise KeyError('This is a set of forms (MultiModelForm), which should contain the number of order forms, '
                           'this is the number that must be explicitly (via the kwargs dictionary,'
                           ' quantity_orders=<number> ) passed when calling the form.')
        AddOrderInBasketSet = formset_factory(AddOrderInBasket, extra=kwargs.pop('quantity_orders'), can_delete=True)
        OrderCreationMultiForm.form_classes['orders'] = AddOrderInBasketSet
        super(OrderCreationMultiForm, self).__init__(*args, **kwargs)

    def is_valid(self):
        return self['order_form'].is_valid() and self['orders'].is_valid()

    def save(self, commit=True):
        order_form_number = self['order_form'].save()
        for product_order in self['orders']:
            product_order.save(order_form_number=order_form_number)
        return order_form_number
