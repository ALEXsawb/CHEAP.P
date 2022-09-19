import json

from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, FormView, View
from django.contrib import messages

from .forms import *
from .models import *
from .services import *


class CheapSh0peHome(ListView):
    model = Collection
    context_object_name = 'hot_collection'
    template_name = 'online_store/home.html'

    def get_queryset(self):
        return get_hot_collection()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['css'] = 'home.css'
        context['hot_collection_products'] = context['hot_collection'].get_products_this_collection()
        context['top_clothing'] = get_top_clothing()
        context['title'] = 'Home'
        return context


class CheapSh0peProduct(DetailView):
    model = Product
    template_name = 'online_store/product_card.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'
    allow_empty = False

    def get_queryset(self):
        return get_product_by_slug_with_collection_and_type_data(self.kwargs['product_slug'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['css'] = 'product_card.css'
        context['title'] = context['object'].name + ' | ' + context['object'].collection.name
        return context

    def post(self, request, *args, **kwargs):
        page = get_page(self.kwargs['collection_slug'], CheapSh0peCatalog.paginate_by) + 1
        response = HttpResponseRedirect(f"/catalog?page={page}#{kwargs['collection_slug']}|{kwargs['product_slug']}")
        basket = get_basket_from_cookies(request)
        basket = add_product_in_basket_or_update_data(basket, request.POST)
        response.set_cookie('basket', json.dumps(basket))
        return response


class CheapSh0peCatalog(ListView):
    model = Collection
    template_name = 'online_store/catalog.html'
    context_object_name = 'catalog'
    allow_empty = False
    per_page = 1
    paginate_by = 3

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__all_public_collections = get_all_public_collections()
        self.__catalog = get_catalog()

    def get_queryset(self):
        return self.__catalog

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_public_collections'] = self.__all_public_collections
        context['css'] = 'catalog.css'
        context['max_product_price'] = get_max_price_catalog(self.__catalog)
        context['title'] = 'Catalog'
        return context


class CheapSh0peCollection(CollectionMixin, DetailView):
    model = Collection
    template_name = 'online_store/collection.html'
    slug_url_kwarg = 'collection_slug'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collection'] = context['object'].get_products_this_collection()
        context['max_product_price'] = get_collection_max_price(context['collection'])
        context['title'] = 'collection: ' + context['object'].name
        context_from_mixin = self.get_user_context()
        return dict(list(context.items()) + list(context_from_mixin.items()))


class CheapSh0peCollections(CollectionMixin, ListView):
    model = Collection
    template_name = 'online_store/collections.html'
    allow_empty = False
    per_page = 1

    def post(self, request, *args, **kwargs):
        try:
            context = get_context_by_filter(request)
        except FilteringError:
            return redirect('catalog')
        context_from_mixin = self.get_user_context()
        context = dict(list(context.items()) + list(context_from_mixin.items()))
        context['title'] = 'Filtered Catalog'
        return render(request, self.template_name, context=context)


class CheapSh0peBasket(FormView):
    template_name = 'online_store/basket.html'
    form_class = OrderCreationMultiForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        self.__get_basket = basket_formation(get_basket_from_cookies(self.request))
        kwargs = super(CheapSh0peBasket, self).get_form_kwargs()
        kwargs['quantity_orders'] = len(self.__get_basket)
        return kwargs

    def post(self, request, *args, **kwargs):
        redirect_to_basket = redirect('basket')
        form = self.get_form()

        if form.is_valid():
            order_form_number = form.save()
            redirect_to_basket.delete_cookie('basket')
            list_id_orders = get_numbers_orders_from_cookies(request)
            list_id_orders.append(order_form_number.pk)
            redirect_to_basket.set_cookie('list_id_orders', json.dumps(list_id_orders))
            return redirect_to_basket
        else:
            return self.form_invalid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['css'] = 'basket.css'
        context['basket'] = join_basket_with_formset_orders(self.__get_basket, context['form']['orders'])
        context['country_numbers'] = PhoneBlank.objects.all()
        context['list_orders'] = get_orders_by_numbers_orders(get_numbers_orders_from_cookies(self.request))
        context['form_for_restore_basket_data'] = SendEmailForm()
        context['title'] = 'basket'
        return context


class RestoreBasketDataByEmail(View):
    def get(self, *args, **kwargs):
        user_orders = get_orders_by_decoded_order_number(**kwargs)
        redirect_to_basket = redirect('basket')
        redirect_to_basket.set_cookie('list_id_orders', json.dumps(user_orders))
        return redirect_to_basket

    def post(self, request):
        form = SendEmailForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            order_number = get_orders_number_by_email(user_email)
            if order_number:
                send_reset_mail(request, user_email, order_number)
                messages.warning(request, 'A message with the restoration of access to order data was sent to the mail')
            else:
                messages.error(request, 'This email has not been used for purchases in the last 30 days')
        else:
            messages.error(request, 'Email not correct, please try again')
        return redirect('basket')


def pageNotFound(request, exception):
    response = render(request, "online_store/error_404.html", context={'error_text': 'PaGe NoT FouND',
                                                                       'css': 'page_not_found.css',
                                                                       'title': 'Error 4O4'})
    response.status_code = 404
    return response
