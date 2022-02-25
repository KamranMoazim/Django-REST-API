
from django.forms import DecimalField
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Value, Func, ExpressionWrapper
from django.db.models.aggregates import Aggregate, Count, Max, Min, Avg
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage

from templated_mail.mail import BaseEmailMessage

from store.models import Collection, Product, OrderItem, Order, Customer
from tags.models import TaggedItem
from .task import notify_customers

# Create your views here.
# request -> response 
# request handler

def hello_world(request):

    # query_set = Product.objects.all()

# lesson 4 ----> Query_Sets
    # few methods return Query_Set and few returns exact result so it depends on the method which you are calling
    # execution of Query_Set
    # way 1
    # for product in quert_set:
    #     pass
    # way 2
    # list(quert_set)
    # way 3
    # quert_set[0]

# lesson 5 ----> Reterieving Objects
    # product = Product.objects.get(pk=2)
    # but you can use pk as we dont know whether id is the primary key or code is primary key or something else is primary key
    # so it is always a better option to use pk instead of id

    # get(pk=2) ---> get will raise exception if the product do not found in DB so we wrap it in try-catch block
    # try:
    #     product = Product.objects.get(pk=2)
    # except ObjectDoesNotExist:
    #     pass

    # else we can also use a cleaner way to do above task
    # product = Product.objects.filter(pk=2).first()
    # or 
    # exists = Product.objects.filter(pk=2).exists()
    # filter --> it returns query_set and executed by other methods like first or exists

# lesson 6 ----> Filtering Objects
    # query_set = Product.objects.filter(unit_price=20)  # it will return a query with all products price equal to 20
    # query_set = Product.objects.filter(unit_price__gt=20)  # it will return a query with all products price greater than 20
    # query_set = Product.objects.filter(unit_price__range=(20, 30))  # it will return a query with all products price range 20 to 30
    # query_set = Product.objects.filter(collection__id=6)  # it will return a query with all products for collection 6
    # query_set = Product.objects.filter(collection__id__in=(1,2,3))  # it will return a query with all products for collection 1, 2, 3
    # query_set = Product.objects.filter(title__contains="coffee")  # it will return a query with all products for title containing coffee  
    # above query is case sensitive and following is not case sensitive-->
    # query_set = Product.objects.filter(title__icontains="coffee")
    # query_set = Product.objects.filter(last_update__year=2020)   # retrun all product updated in 2020
    # query_set = Product.objects.filter(description__isnull=True)  # return if any product's descriptiton is null 

# lesson 7 ---> Complex Lookups Using Q Objects
    # a query to get products inventoy less than 10 **AND** unit_price less than 20 
    # query_set = Product.objects.filter(inventory__lt=10, unit_price__lt=20)
    # same above query in other form
    # query_set = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)

    # to apply **OR** operator we ave to use Q from django
    # a query to get products inventoy less than 10 **OR** unit_price less than 20 
    # query_set = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))
    # a query to get products inventoy less than 10 **OR** unit_price **NOT** less than 20 
    # query_set = Product.objects.filter(Q(inventory__lt=10) | ~Q(unit_price__lt=20))

# lesson 8 ---> Referencing Fields using F Objects 
    # query_set = Product.objects.filter(inventory=F("unit_price"))  # here we are saying get all those product where inventory is equal to unit_price
    # query_set = Product.objects.filter(inventory=F("collection__id"))  # here we are saying get all those product where inventory is equal to collection_id

# lesson 9 ---> sorting data
    # query_set = Product.objects.order_by("title")  # sorting in Ascending Order by title
    # query_set = Product.objects.order_by("-title")  # sorting in Descending Order by title
    # query_set = Product.objects.order_by("unit_price", "-title")  # sorting in Ascending Order by unit_price and then Descending Order by title
    # query_set = Product.objects.filter(collection__id=6).order_by("unit_price", "-title").reverse()
    # products_not_query_set = Product.objects.order_by("unit_price", "-title").reverse()[0:10]
    # there are also methods latest and earliest

# lesson 10 ---> limiting data
    # query_set = Product.objects.all()[:5]  # to get first 5 object
    # query_set = Product.objects.all()[5:5]  # to get next 5 object


# lesson 11 ---> seleting fields
    # query_set = Product.objects.values("id", "title")   # read only id and title of product
    # query_set = Product.objects.values("id", "title", "collection__title")   # read only id and title of product and collection title
    # query_set = Product.objects.values_list("id", "title", "collection__title")   # it returns tuple because above was returning objects 
    # EXERCISE   -->  select product that have been ordered and sort them by their title
    # query_set = OrderItem.objects.values("product__id").distinct()
    # query_set = Product.objects.filter(id__in=query_set).order_by("title")


# lesson 12 ---> deferring field
    # query_set = Product.objects.only("id", "title")
    # query_set = Product.objects.defer("id", "title")
    # DONT use above two when you dont know what are you doing

# lesson 13 ---> selecting related objects
    # select_related ----> used when other end has 1 object like 1-to-1 relations
    # prefetch_related --> used when other end has n object like 1-to-n relations
    # query_set = Product.objects.select_related("collection").all()
    # query_set = Product.objects.prefetch_related("promotions").all()
    # query_set = Product.objects.prefetch_related("promotions").select_related("collection").all()
    # EXERCISE   -->  get last 5 orders by with their customers and items and (inclu products)
    # oquery_set = Order.objects.select_related("customer").order_by("-placed_at")[:5]
    # oquery_set = oquery_set.prefetch_related("orderitem_set__product").prefetch_related("")
    # "orders":list(oquery_set)

# lesson 14 ---> aggregating object
    # result = Product.objects.aggregate(Count("id")) # gives total number of products in DB
    # result = Product.objects.aggregate(count=Count("id"), min_price=Min("unit_price")) # gives total number of products in DB and min price
    # result = Product.objects.filter(collection__id=6).aggregate(count=Count("id"), min_price=Min("unit_price")) # gives total number of products in DB and min price
    # print(result)

# lesson 15 ---> annotating object
    # query_set = Customer.objects.annotate(is_new=Value(True))  # it adds new column in the coming result --> is_new
    # query_set = Customer.objects.annotate(new_id=F("id")+3)  # it adds new column in the coming result --> new_id+3

# lesson 16 ---> Database Functions Func
    # query_set = Customer.objects.annotate(full_name=Func(F("first_name"), Value(" "), F("last_name"), function="CONCAT"))
    # query_set = Customer.objects.annotate(full_name=Concat("first_name", Value(" "), "last_name"))

# lesson 17 ---> Grouping Data
    # query_set = Customer.objects.annotate(orders_count=Count("order"))   # here should be order_set but its not working, Dont know why

# lesson 18 ---> Expression Wrappers
    # discounted_price_ex = ExpressionWrapper(F("unit_price")*0.8, output_field=DecimalField())
    # query_set = Customer.objects.annotate(discounted_price=discounted_price_ex)

# lesson 19 ---> Querying Generic Relations
    # content_type = ContentType.objects.get_for_model(Product)
    # query_set = TaggedItem.objects.select_related("tag").filter(content_type=content_type, object_id=1)

# lesson 20 ---> Custom Managers
    # query_set = TaggedItem.objects.get_tags_for(Product, 2)

# lesson 21 ---> QuerySet Cache
    # query_set = Product.objects.all()
    # list(quert_set)  # 1
    # quert_set[0]     # 2
    # query 1 will be executed first and then query 2 will be executed
    # but query 2 will take less time as first query will store in query cache.

# lesson 22 ---> Creating Objects
    # way 1   --> this is best approach
    # collection = Collection()
    # collection.title = "Shoes"
    # collection.featured_product = Product(pk=3)   # way-1
    # # collection.featured_product_id = 3            # way-2
    # collection.save()

    # way 2
    # collection = Collection(title="Shoes", featured_product=1)
    # collection.save()

    # way 3
    # Collection.objects.create(title="Shoes", featured_product=1)

# lesson 23 ---> Updating Objects
    # way 1 ---> if you are using this approach then make sure you update all fields 
    # if not then DO-NOT use this method
    # else it will make other fields empty  
    # collection = Collection(pk=3)
    # collection.title = "New Shoes"
    # collection.featured_product = Product(pk=3)   # way-1
    # collection.save()

    # way 2
    # collection = Collection.objects.get(pk=3)  # this will not have the above discussed problem
    # collection.featured_product = Product(pk=3)   # way-1
    # collection.save()

    # way 3
    # Collection.objects.filter(pk=3).update(featured_product=None)

# lesson 24 ---> Deleting Objects
    # deleting single item
    # collection = Collection(pk=13)
    # collection.delete()

    # deleting multiple items
    # Collection.objects.filter(id__lt=5).delete()

# lesson 25 ---> Transactions
    # with transaction.atomic():
    #     order = Order()
    #     order.customer_id=3
    #     order.save()

    #     item = OrderItem()
    #     item.order = order
    #     item.product_id = 5
    #     item.quantity = 2
    #     item.unit_price = 23.5
    #     item.save()
    
# lesson 26 ---> RAW SQL Queries
    # query_set = Collection.objects.raw("SELECT * from store_collection")



# EMAIL SENDING LESSON START
    # return render(request, "index.html", {"name":"Kamran Moazim", "products":list(query_set)})
    # return render(request, "index.html", {"name":"Kamran Moazim", "products":products_not_query_set})

    # try:
    #     # way 1
    #     send_mail('subject', 'message', 'kamrannaseer76543@gmail.com', ["to@gmail.com"])
    #     # mail_admins('subject', 'message', html_message="same message again")

    #     # way 2
    #     # message = EmailMessage('subject', 'message', 'kamrannaseer76543@gmail.com', ["to@gmail.com"])
    #     # message.attach_file("playground/static/images/bootstrap.png")
    #     # message.send()

    #     # way 3
    #     # message = BaseEmailMessage(template_name="email/hello.html", context={"name":"Kamran"})
    #     # message.send(["to@gmail.com"])
    # except BadHeaderError:
    #     pass

# BACKGROUND RUNNING TASKS LESSON
    notify_customers.delay("This is message")

    return render(request, "index.html")




@transaction.atomic()   # this is to make complete function atomic
def try_atomi(request):
    order = Order()
    order.customer_id=3
    order.save()

    item = OrderItem()
    item.order = order
    item.product_id = 5
    item.quantity = 2
    item.unit_price = 23.5
    item.save()

    return render(request, "index.html", {"name":"Kamran Moazim", "order":order})