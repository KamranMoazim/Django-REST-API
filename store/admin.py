
from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.db.models.query import QuerySet


# Register your models here.
from . import models


admin.site.register(models.Cart)


class OrderItemInline(admin.StackedInline):   # admin.TabularInline
    model = models.OrderItem
    extra = 0
    min_num = 1
    max_num = 10
    autocomplete_fields = ["product"]


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "placed_at", "payment_status", "customer"]
    autocomplete_fields = ["customer"]
    inlines = [OrderItemInline]


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "total_order"]
    list_editable = ["membership"]
    list_per_page = 10
    ordering = ["user__first_name", "user__last_name"]
    list_select_related = ["user"]
    search_fields = ["user__first_name__istartswith", "user__last_name__istartswith"]
    autocomplete_fields = ["user"]

    @admin.display(ordering="total_order")
    def total_order(self, customer):
        # return customer.total_order
        # url = reverse("admin:store_order_changelist")     # reverse("admin:app_model_page")
        url = reverse("admin:store_order_changelist") + "?" + urlencode({ "customer__id" : str(customer.id) })
        return format_html(f"<a href='{url}'> {customer.total_order} </a>")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(total_order=Count("order"))


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"
    
    def lookups(self, request, model_admin):
        return [
            ("<10", "Low")
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)
         

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']
    
    def thumbnail(self, instance):
        if instance.image.name != "":
            return format_html(f"<img class='thumbnail' src='{instance.image.url}' />")
        return ""


# way 1
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    # fields = ["title", "unit_price"]
    # exclude = ["title", "description"]
    # readonly_fields = ["title"]

    prepopulated_fields = {
        "slug":["title"]
    }
    autocomplete_fields = ["collection"]
    actions = ["clear_inventory"]
    # inlines = [ProductImageInlines]
    list_display = ["title", "unit_price", "inventory_status", "collection_title"]
    list_editable = ["unit_price"]
    list_filter = ["collection", "last_update", InventoryFilter]
    list_per_page = 10
    list_select_related = ["collection"]
    search_fields = ["title"]
    
    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        if product.inventory < 10:
            return "Low"
        return "OK"

    @admin.action(description="Clear Inventory!")
    def clear_inventory(self, request, queryset:QuerySet):
        inventory_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f" {inventory_count} Products Inventory Cleared out Successfully!",
            messages.WARNING
        )

    class Media:
        css = {
            'all':["store/styles.css"]
        }

# way 2
# admin.site.register(models.Product, ProductAdmin)

# admin.site.register(models.Collection)
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products_count"]
    search_fields = ["title"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        # return collection.products_count
        # url = reverse("admin:store_product_changelist")     # reverse("admin:app_model_page")
        url = reverse("admin:store_product_changelist") + "?" + urlencode({ "collection__id" : str(collection.id) })
        return format_html(f"<a href='{url}'> {collection.products_count} </a>")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('products'))
