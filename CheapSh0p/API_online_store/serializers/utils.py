from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _
from CheapSh0p.settings import STANDARD_SIZES


class UpdateNestedObjectError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Error update nested object')
    default_code = 'error'

    def __init__(self, *args, **kwargs):
        field_name = kwargs['field_name']
        self.detail = (f'For update {field_name} data, you should come to {field_name} page, but if you need to '
                       f'replace {field_name} instance referenced by the product instance, then you need to replace '
                       f'collection name with the name of the desired {field_name} instance')


def get_name_and_url_object(self, obj, callable_attr_name: str):
    try:
        callable_attr = getattr(obj, callable_attr_name)
    except AttributeError:
        callable_attr = obj
    return {'name': callable_attr.name if 'name' in callable_attr.__dir__() else callable_attr.type,
            'url': reverse(f'{callable_attr_name}-detail', kwargs={'slug': callable_attr.slug},
                           request=self.context['request'])}


def update_nested_object_data(instance, attribute_name: str, model, slug) -> None:
    try:
        setattr(instance, attribute_name, model.objects.get(slug=slug))
        instance.save()
    except model.DoesNotExist:
        raise UpdateNestedObjectError(field_name=attribute_name)


def get_correct_sizes_from_list(sizes: list) -> str:
    if STANDARD_SIZES[STANDARD_SIZES.index(sizes[0]):] == sizes:
        return f'{sizes[0]}-{sizes[-1]}'
    elif len(STANDARD_SIZES) > len(sizes) > 2:
        len_difference = len(STANDARD_SIZES) - len(sizes)
        for number_movie in range(len_difference):
            if STANDARD_SIZES[number_movie:-len_difference - number_movie:] == sizes:
                return f'{sizes[0]}-{sizes[-1]}'
    return ','.join(sizes)
