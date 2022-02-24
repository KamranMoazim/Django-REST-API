
from django.urls import path, include
# from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers

from . import views


# router = DefaultRouter()   # SimpleRouter()
router = routers.DefaultRouter()   # routers.SimpleRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet)

nestRouter = routers.NestedDefaultRouter(router, "products", lookup="product")  # means product_pk to get product id
nestRouter.register("reviews", views.ReviewViewSet, basename="product-reviews")

# print(router.urls)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(nestRouter.urls))
]

# urlpatterns = [
#     path('products/', views.ProductList.as_view()),
#     path('products/<int:pk>/', views.ProductDetail.as_view),
#     path('collections/', views.CollectionList.as_view()),
#     path('collections/<int:pk>/', views.CollectionDetail.as_view(), name="collection-detail"),
# ]
