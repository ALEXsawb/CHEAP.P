from django.urls import path
from .views import *
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(60*60*24*7)(CheapSh0peHome.as_view()), name='home'),
    path('catalog', cache_page(60*60)(CheapSh0peCatalog.as_view()), name='catalog'),
    path('catalog/collections', CheapSh0peCollections.as_view(), name='collections'),
    path('catalog/<slug:collection_slug>', cache_page(60*5)(CheapSh0peCollection.as_view()), name='collection'),
    path('catalog/<slug:collection_slug>/<slug:product_slug>', cache_page(60)(CheapSh0peProduct.as_view()),
         name='product'),
    path('basket', CheapSh0peBasket.as_view(), name='basket'),
    path('basket/<uidb64>/', RestoreBasketDataByEmail.as_view(), name='restore_basket_data'),
    path('basket/restore_data', RestoreBasketDataByEmail.as_view(), name='get_email_for_restore_basket_data')
]
