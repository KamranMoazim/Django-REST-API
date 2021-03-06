from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

import debug_toolbar

admin.site.site_header = "My Store Front"
admin.site.site_title = "My Store Front"
admin.site.index_title = "This is sub Title"



urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
    path('auth/', include("djoser.urls")),
    path('auth/', include('djoser.urls.jwt')),

    path('playground/', include("playground.urls")),
    path('store/', include("store.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 