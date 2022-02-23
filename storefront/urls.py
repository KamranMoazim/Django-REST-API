
import debug_toolbar
from django.contrib import admin
from django.urls import path, include


admin.site.site_header = "My Store Front"
admin.site.site_title = "My Store Front"
admin.site.index_title = "This is sub Title"



urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),

    path('playground/', include("playground.urls")),
    path('store/', include("store.urls")),
]
