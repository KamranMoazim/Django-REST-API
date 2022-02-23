
from decimal import Decimal
from rest_framework import serializers

from store.models import Collection, Product


# serializers are actually for outer world
# means what you wants to show to outer world


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "title", "products_count"]
    
    products_count = serializers.IntegerField(read_only=True)

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "slug", "description", "inventory", "unit_price", "price_with_tax", "collection"] 
        # fields = "__all__"   # for getting all fields

    price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")
    
    def calculate_tax(self, product:Product):
        # print("+++++++++++++++++++++++++++", product.unit_price)
        return product.unit_price * Decimal(1.1)


    # following method is over-ride for the case if we wants to store some other values also --- similarly you can also over ride update method
    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     product.anyOtherField = 1
    #     product.save()
    #     return product

    # following validation is for the case in which you want validation other than only database validation 
    # def validate(self, data):
    #     if data["password"] != data["confirm_password"]:
    #         return serializers.ValidationError("Passwords do not match")
    #     return data


# ++++++++++++++++++++++++++++++++++++++++++++++++++++

# class CollectionSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField()

# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(max_digits=6, decimal_places=2, source="unit_price")
#     price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")
#     # way 1
#     # collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
#     # way 2
#     # collection = serializers.StringRelatedField()
#     # way 3
#     # collection = CollectionSerializer()
#     # way 4
#     collection = serializers.HyperlinkedRelatedField(queryset=Collection.objects.all(), view_name='collection-detail')   # way 4
#     def calculate_tax(self, product:Product):
#         return product.unit_price * Decimal(1.1)