from math import prod
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

from .models import Collection, Product
from .serializers import ProductSerializer, CollectionSerializer


@api_view(["GET", "POST"])
def product_list(request):
    if request.method == "GET":
        queryset = Product.objects.select_related("collection").all()
        seriazler = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(seriazler.data)
    elif request.method == "POST":
        # way 1
        # serializer = ProductSerializer(data=request.data)
        # if serializer.is_valid(raise_exception=True):
        #     serializer.validated_data
        #     return Response("ok")
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # way 2
        serializer = ProductSerializer(data=request.data)
        # print("**********************", request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # print(serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET", "PUT", "DELETE"])
def product_detail(request, pk):

    # way 1
    # try:
    #     product = Product.objects.get(pk=pk)
    #     seriazler = ProductSerializer(product)
    #     return Response(seriazler.data)
    # except Product.DoesNotExist:
    #     return Response(status=status.HTTP_404_NOT_FOUND)

    # way 2
    # product = get_object_or_404(Product, pk=pk)
    # seriazler = ProductSerializer(product)
    # return Response(seriazler.data)
    
    product = get_object_or_404(Product, pk=pk)
    if request.method == "GET":
        seriazler = ProductSerializer(product)
        return Response(seriazler.data)
    elif request.method == "PUT":
        seriazler = ProductSerializer(product, data=request.data)
        seriazler.is_valid(raise_exception=True)
        seriazler.save()
        return Response(seriazler.data)
    elif request.method == "DELETE":
        if product.orderitems.count() > 0:
            return Response({"error":"This Product is Associated with Order/s!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response({"message":"Product Deleted Successfully!"}, status=status.HTTP_204_NO_CONTENT)





@api_view(["GET", "POST"])
def collection_list(request):
    if request.method == "GET":
        queryset = Collection.objects.annotate(products_count=Count('products')).all()
        seriazler = CollectionSerializer(queryset, many=True, context={'request': request})
        return Response(seriazler.data)
    elif request.method == "POST":
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(["GET", "PUT", "DELETE"])
def collection_detail(request, pk):
    collection = get_object_or_404(Collection.objects.annotate(products_count=Count('products')), pk=pk)
    if request.method == "GET":
        seriazler = CollectionSerializer(collection)
        return Response(seriazler.data)
    elif request.method == "PUT":
        seriazler = CollectionSerializer(collection, data=request.data)
        seriazler.is_valid(raise_exception=True)
        seriazler.save()
        return Response(seriazler.data)
    elif request.method == "DELETE":
        if collection.products.count() > 0:
            return Response({"error":"This Collection is Associated with Products!"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response({"message":"Collection Deleted Successfully!"}, status=status.HTTP_204_NO_CONTENT)

