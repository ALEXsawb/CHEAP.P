from django.contrib import admin
from django.urls import path, include
from CheapSh0p import settings
from django.conf.urls.static import static
import debug_toolbar
from online_store.views import pageNotFound

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('online_store.urls')),
    path('api/v1/', include('API_online_store.urls')),
]


if settings.DEBUG:
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = pageNotFound
