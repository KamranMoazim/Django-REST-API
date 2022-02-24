
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from django.contrib import admin

from uuid import uuid4


# Create your models here.

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
    # here we will have a field 'product_set' 
    # ---> or 'products' as chnaged in Product promotions 


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey("Product", on_delete=models.SET_NULL, null=True, related_name="+")
    # we used ---> related_name="+"  because as by-default django is going to create reverse relation named --> collection
    # so we override it and said django to not create Reverse relation   

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        ordering = ["title"]


class Product(models.Model):
    # sku = models.CharField(max_length=10, primary_key=True)    
    #### we dont need above thing, it will be automatically created by Django
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    last_update = models.DateTimeField(auto_now=True)
    # a collection can have multiple Products
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name="products")
    # many products can have many promotions
    promotions = models.ManyToManyField(Promotion, related_name='products', blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]

    # first_name = models.CharField(max_length=255)
    # last_name = models.CharField(max_length=255)
    # email = models.EmailField(unique=True)
    # as above fields exists in our model so dont need this
    phone = models.CharField(max_length=22)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

    @admin.display(ordering="user__first_name")
    def first_name(self) -> str:
        return f"{self.user.first_name}"

    @admin.display(ordering="user__last_name")
    def last_name(self) -> str:
        return f"{self.user.last_name}"

    class Meta:
        ordering = ["user__first_name", "user__last_name"]



# a customer can have only ONE address means one-to-one relationship
# class Address(models.Model):
#     street = models.CharField(max_length=255)
#     city = models.CharField(max_length=255)
#     customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip = models.CharField(max_length=25)
    customer = models.ForeignKey(Customer, related_name="customer", on_delete=models.CASCADE)


class Order(models.Model):
    STATUS_PENDING = 'P'
    STATUS_COMPLETE = 'C'
    STATUS_FAILED = 'F'
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETE, "Complete"),
        (STATUS_FAILED, "Failed"),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING)
    # a customer can have multiple Orders
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        permissions = [
            ('cancer_order', "Can Cancel Order")
        ]


class OrderItem(models.Model):
    # a order can have multiple OrderItems
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    # a product can blong multiple OrderItems
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orderitems")
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)








class Cart(models.Model):
    id  = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    # a cart can have multiple CartItems
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items") # cartitem_set
    # a product can blong multiple CartItems
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [["cart", "product"]]


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
