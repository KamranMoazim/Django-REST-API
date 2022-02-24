from math import prod
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

from django_filters.rest_framework import DjangoFilterBackend
from .pagination import MyDefaultPaginationClass

# Create your views here.

from .models import Collection, OrderItem, Product, Review
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer
from .filters import ProductFilter


class ReviewViewSet(ModelViewSet):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id":self.kwargs["product_pk"]}
    





# *********** IMPLEMENTATION *********** USING APIView
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ["collection_id", "unit_price"]
    filterset_class = ProductFilter
    # pagination_class = PageNumberPagination
    pagination_class = MyDefaultPaginationClass
    search_fields = ["title", "description"]
    ordering_fields = ["unit_price", "last_update"]

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



