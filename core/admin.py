from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline

# Register your models here.
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem
from core.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name'),
        }),
    )


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
