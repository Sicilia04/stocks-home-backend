from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "barcode", "category", "min", "quantity"]
    search_fields = ["name", "barcode", "category"]
