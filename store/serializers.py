
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from store.models import Collection, Customer, Product, Review, Cart, CartItem, Order, OrderItem
from .signals import order_created

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




# &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']



# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "unit_price"] 


class OrderSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ["id", "placed_at", "payment_status", "customer", "items"] 



class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]
            user_id = self.context["user_id"]
            # (customer, created) = Customer.objects.get_or_create(user_id=user_id)
            # as we are using signals so we can use these changings
            customer = Customer.objects.get(user_id=user_id)
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            order_items = [ OrderItem(order=order, product=item.product, unit_price=item.product.unit_price, quantity=item.quantity) for item in cart_items ]

            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)

            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']
