from statistics import mode
from django.db import models

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


class Product(models.Model):
    # sku = models.CharField(max_length=10, primary_key=True)    
    #### we dont need above thing, it will be automatically created by Django
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    # a collection can have multiple Products
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    # many products can have many promotions
    promotions = models.ManyToManyField(Promotion, related_name='products')


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=22)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)


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


class OrderItem(models.Model):
    # a order can have multiple OrderItems
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    # a product can blong multiple OrderItems
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)








class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    # a cart can have multiple CartItems
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    # a product can blong multiple CartItems
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()