
from decimal import Decimal
from venv import create
from rest_framework import serializers

from store.models import Collection, Product, Review, Cart, CartItem


# serializers are actually for outer world
# means what you wants to show to outer world






class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "name", "description", "date"]  #  "product", 

    def create(self, validated_data):
        return Review.objects.create(product_id=self.context["product_id"], **validated_data)


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



# CART SECTION STARTED HERE ************************************************************
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "unit_price"]



class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name="calculate_total")
    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]

    def calculate_total(self, cart_items:CartItem):
        return cart_items.quantity * cart_items.product.unit_price


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name="get_total")
    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]

    def get_total(self, cart:Cart):
        return sum([cart_item.quantity * cart_item.product.unit_price for cart_item in cart.items.all()])




class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Invalid Product ID.")
        return value

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

    # we are usign self.instance becasue it is implemented in ModelSerializer 
    # so to make everything working as they were previously we have to do this 
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # self.instance = CartItem.objects.create(cart_id=cart_id, product_id=product_id, quantity=quantity)
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']