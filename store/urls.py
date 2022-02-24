
from django.urls import path, include
# from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers

from . import views


# router = DefaultRouter()   # SimpleRouter()
router = routers.DefaultRouter()   # routers.SimpleRouter()
router.register("products", views.ProductViewSet, basename="products")
router.register("collections", views.CollectionViewSet)
router.register("carts", views.CartViewSet, basename="carts")
router.register("customers", views.CustomerViewSet, basename="customers")

products_router = routers.NestedDefaultRouter(router, "products", lookup="product")  # means product_pk to get product id
products_router.register("reviews", views.ReviewViewSet, basename="product-reviews")

carts_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")       # means cart_pk to get cart id
carts_router.register("items", views.CartItemViewSet, basename="cart-items")

# print(router.urls)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(products_router.urls)),
    path("", include(carts_router.urls))
]

# urlpatterns = [
#     path('products/', views.ProductList.as_view()),
#     path('products/<int:pk>/', views.ProductDetail.as_view),
#     path('collections/', views.CollectionList.as_view()),
#     path('collections/<int:pk>/', views.CollectionDetail.as_view(), name="collection-detail"),
# ]
