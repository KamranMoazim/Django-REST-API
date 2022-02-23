
from django.contrib import admin

# Register your models here.
from . import models



@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["label"]
    search_fields = ["label"]

