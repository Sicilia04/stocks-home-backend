from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Category, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "products_count", "created", "modified"]
    search_fields = ["name", "slug"]

    @admin.display(description=_("Products"), boolean=False)
    def products_count(self, obj: Category) -> int:
        return obj.products.count()


class StockMovementInline(admin.TabularInline):
    # Permet d'ajouter des mouvements de stock depuis la page produit.
    # L'historique (horodatés par le modèle) reste en lecture seule.
    model = StockMovement
    fields = ["kind", "quantity", "created"]
    readonly_fields = ["created"]
    extra = 0
    max_num = 5


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "barcode",
        "category",
        "quantity",
        "min_quantity",
        "is_low_stock",
        "is_active",
        "modified",
    ]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "barcode", "category__name"]
    autocomplete_fields = ["category"]
    readonly_fields = ["created", "modified"]
    inlines = [StockMovementInline]

    @admin.display(description=_("Low stock"), boolean=True)
    def is_low_stock(self, obj: Product) -> bool:
        return obj.is_low_stock


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    # Lecture seule : les mouvements s'ajoutent depuis la page produit,
    # l'historique existant ne doit jamais être modifiable.
    list_display = ["id", "product", "kind", "quantity", "created"]
    list_filter = ["kind", "product__category"]
    search_fields = ["product__name", "product__barcode"]
    readonly_fields = ["product", "kind", "quantity", "created", "modified"]

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
