from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline

# Register your models here.
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem


class TagInline(GenericTabularInline):   # GenericStackedInline
    model = TaggedItem
    extra = 0
    min_num = 1
    max_num = 10
    autocomplete_fields = ["tag"]

class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]

admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)
