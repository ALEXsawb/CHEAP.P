from django import template
register = template.Library()


@register.filter
def from_label_to_span_text(label):
    return label.split(" ")[0]


@register.filter
def from_label_to_h5_text(label):
    label_splt = label.split(" ")
    if len(label_splt) > 1:
        h5 = ' '.join(label_splt[1:])
        return h5
    return " "


@register.simple_tag
def new_variable(variable):
    return variable


@register.simple_tag
def show_categories(product):
    form = product.form
    form.fields['quantity'].widget.attrs.update(value=product.quantity)
    form.fields['color'].widget.attrs.update(value=product.color)
    form.fields['size'].widget.attrs.update(value=product.size)
    form.fields['product'].widget.attrs.update(value=product.pk)
    return form


@register.simple_tag
def set_int_field_value(value):
    print("__", value)
