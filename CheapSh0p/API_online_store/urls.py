from django.urls import path, include, re_path
from .views import *
from rest_framework import routers


router = routers.SimpleRouter(trailing_slash=False)
router.register(r'type', TypeClothingAPI, basename='type')
router.register(r'catalog', CollectionAPI, basename='collection')

urlpatterns = [
    path('drf-auth/', include('rest_framework.urls')),
    path(r'catalog', CatalogAPI.as_view(), name='catalog-list'),
    path(r'types', TypeClothingListAPI.as_view(), name='types-list'),
    path(r'catalog/<str:collection_slug>/<str:slug>', ProductAPI.as_view(), name='product-detail'),
    path('', include(router.urls)),

    re_path(r'^auth/', include('djoser.urls.authtoken')),
]