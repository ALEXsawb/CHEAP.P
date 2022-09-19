from online_store.models import Product, Collection
from online_store.services.views import set_views_for_collection, set_views_for_product


class BaseMiddlewareViews:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response


class MiddlewareForAddingViews(BaseMiddlewareViews):
    def process_template_response(self, request, response):
        resolver_match = request.resolver_match

        if resolver_match.url_name == 'collection':
            collection_slug = resolver_match.kwargs['collection_slug']
            set_views_for_collection(Collection.objects.filter(slug=collection_slug))

        elif resolver_match.url_name == 'product':
            product_slug = resolver_match.kwargs['product_slug']
            set_views_for_product(Product.objects.select_related('type').filter(slug=product_slug))
        return response
