
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import IsAdminOrReadOnly, MyFullDjangoModelPermissions, ViewCustomerHistoryPermission
from .pagination import MyDefaultPaginationClass

# Create your views here.

from .models import CartItem, Collection, Order, OrderItem, Product, Review, Cart, Customer, ProductImage
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer,\
      CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, \
      CustomerSerializer, OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer, \
      ProductImageSerializer
from .filters import ProductFilter





class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id":self.kwargs["product_pk"]}





class OrderViewSet(ModelViewSet):
    # queryset = Order.objects.all()
    # serializer_class = OrderSerializer

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id':self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.id is None:
            return Response("Please Login!")
        if self.request.user.is_staff:
            return Order.objects.all()
        # (customer_id, created) = Customer.objects.only("id").get_or_create(user_id=self.request.user.id)
        # as we are using signals so we can use these changings
        customer_id = Customer.objects.only("id").get(user_id=self.request.user.id)
        if self.request.method == "GET":
            return Order.objects.filter(customer_id=customer_id) 



# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@





# class CustomerViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]
    # permission_classes = [MyFullDjangoModelPermissions]

    # def get_permissions(self):  # for over-riding permission for particular method like GET, POST, DELETE 
    #     if self.request.method == "GET":
    #         return [AllowAny()]
    #     return [IsAuthenticated()]

    # detail=True ---> means route will be like this http://127.0.0.1:8000/store/customers/1/history/
    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response("ok")

    # detail=False ---> means route will be like this http://127.0.0.1:8000/store/customers/me
    @action(detail=False, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])   # if you wants to over-ride permission for particular action
    def me(self, request):
        if request.user.id is None:
            return Response("Please Login!")
        # (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
        # as we are using signals so we can use these changings
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)



# &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&


class CartItemViewSet(ModelViewSet):
    # queryset = CartItem.objects.all()
    # serializer_class = CartItemSerializer
    http_method_names = ['get', 'post', 'patch', 'delete',]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer



    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related("product")

    def get_serializer_context(self):
        return {"cart_id":self.kwargs["cart_pk"]}



class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related("items__product").all()
    serializer_class = CartSerializer


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id":self.kwargs["product_pk"]}
    





# *********** IMPLEMENTATION *********** USING APIView
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("images").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ["collection_id", "unit_price"]
    filterset_class = ProductFilter
    # pagination_class = PageNumberPagination
    pagination_class = MyDefaultPaginationClass
    search_fields = ["title", "description"]
    ordering_fields = ["unit_price", "last_update"]

    def get_permissions(self):
        return [IsAdminOrReadOnly()]

# we donot need following custom filter as we are using library now 
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get("collection_id")
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset
    
    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs["pk"]).count() > 0:
            return Response({"error":"This Product is Associated with Order/s!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)




# *********** IMPLEMENTATION *********** USING ListCreateAPIView and RetrieveUpdateDestroyAPIView
# class ProductList(ListCreateAPIView):
#     # way 1 ----> simple way
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     # way 2 ----> if you want some modification or some action
#     # def get_queryset(self):
#     #     return Product.objects.all()
#     # def get_serializer_class(self):
#     #     return ProductSerializer
#     def get_serializer_context(self):
#         return {'request': self.request}
# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response({"error":"This Product is Associated with Order/s!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response({"message":"Product Deleted Successfully!"}, status=status.HTTP_204_NO_CONTENT)
    



# ++++++++++++++++++++++++++++++




# *********** IMPLEMENTATION *********** USING APIView
# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.select_related("collection").all()
#         seriazler = ProductSerializer(queryset, many=True, context={'request': request})
#         return Response(seriazler.data)
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
# class ProductDetail(APIView):
#     def get(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         seriazler = ProductSerializer(product)
#         return Response(seriazler.data)
#     def put(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         seriazler = ProductSerializer(product, data=request.data)
#         seriazler.is_valid(raise_exception=True)
#         seriazler.save()
#         return Response(seriazler.data)
#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response({"error":"This Product is Associated with Order/s!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response({"message":"Product Deleted Successfully!"}, status=status.HTTP_204_NO_CONTENT)
    


# ******************************************************************************************

# *********** IMPLEMENTATION *********** ModelViewSet
class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs["pk"]).count() > 0:
            return Response({"error":"This Collection is Associated with Products!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)





# *********** IMPLEMENTATION *********** USING ListCreateAPIView and RetrieveUpdateDestroyAPIView
# class CollectionList(ListCreateAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class = CollectionSerializer
#     def get_serializer_context(self):
#         return {'request': self.request}
# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class = CollectionSerializer
#     # lookup_field = 'id'   # if you wants to use id in urls.py rather than pk
#     def delete(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), pk=pk)
#         if collection.products.count() > 0:
#             return Response({"error":"This Collection is Associated with Products!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response({"message":"Collection Deleted Successfully!"}, status=status.HTTP_204_NO_CONTENT)





# ++++++++++++++++++++++++++++++




# *********** IMPLEMENTATION *********** USING APIView
# class CollectionList(APIView):
#     def get(self, request):
#         queryset = Collection.objects.annotate(products_count=Count('products')).all()
#         seriazler = CollectionSerializer(queryset, many=True, context={'request': request})
#         return Response(seriazler.data)
#     def post(self, request):
#         serializer = CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
# class CollectionDetail(APIView):
#     def get(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), pk=pk)
#         seriazler = CollectionSerializer(collection)
#         return Response(seriazler.data)
#     def put(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), pk=pk)
#         seriazler = CollectionSerializer(collection, data=request.data)
#         seriazler.is_valid(raise_exception=True)
#         seriazler.save()
#         return Response(seriazler.data)
#     def delete(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), pk=pk)
#         if collection.products.count() > 0:
#             return Response({"error":"This Collection is Associated with Products!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response({"message":"Collection Deleted Successfully!"}, status=status.HTTP_204_NO_CONTENT)



