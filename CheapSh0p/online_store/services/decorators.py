from django.core.cache import cache


def max_price_from_cache(function_):
    def wrapper(collections: list):
        if cache.get('max_product_price'):
            return str(cache.get('max_product_price'))
        return function_(collections)
    return wrapper
