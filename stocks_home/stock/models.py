from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

# Le code-barres doit correspondre à un EAN-8 (8 chiffres) ou un EAN-13 (13 chiffres).
barcode_validator = RegexValidator(
    regex=r"^(?:\d{8}|\d{13})$",
    message=_("Barcode must be an EAN-8 or EAN-13 (8 or 13 digits)."),
)


class Category(TimeStampedModel):
    """Categorie de produits, nom et slug uniques (trié par nom)."""

    name = models.CharField(_("Name"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    """Produit référencé par un code-barres unique, avec stock et seuil d'alerte."""

    name = models.CharField(_("Name"), max_length=255)
    barcode = models.CharField(
        _("Barcode"),
        max_length=64,
        unique=True,
        validators=[barcode_validator],
    )
    # PROTECT : impossible de supprimer une catégorie qui contient des produits.
    category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        on_delete=models.PROTECT,
        related_name="products",
    )
    # Seuil sous lequel le stock est considéré comme faible.
    min_quantity = models.PositiveIntegerField(
        _("Minimum quantity"), default=0,
    )
    # Quantité en stock ; modifiée en pratique par StockMovement (trace des mouvements).
    quantity = models.PositiveIntegerField(_("Quantity"), default=0)
    # Un produit inactif ne peut plus recevoir de mouvement de stock.
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def is_low_stock(self) -> bool:
        """Vrai si le stock est strictement sous le seuil mini."""
        return self.quantity < self.min_quantity


class StockMovement(TimeStampedModel):
    """Mouvement de stock (entrée/sortie) qui met à jour la quantité du produit.

    L'écriture du mouvement et la mise à jour du stock sont dans la même
    transaction : l'un échoue, tout est annulé.
    """

    class MovementKind(models.TextChoices):
        IN = "in", _("Stock in")
        OUT = "out", _("Stock out")

    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        on_delete=models.CASCADE,
        related_name="movements",
    )
    kind = models.CharField(_("Kind"), max_length=3, choices=MovementKind.choices)
    # MinValueValidator(1) : un mouvement à quantité nulle est refusé par full_clean().
    quantity = models.PositiveIntegerField(
        _("Quantity"), validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = _("Stock movement")
        verbose_name_plural = _("Stock movements")
        # "-pk" rend le tri stable en cas de même horodatage.
        ordering = ["-created", "-pk"]
        # Index pour les requêtes « mouvements d'un produit, triés par date ».
        indexes = [
            models.Index(
                fields=["product", "created"], name="stock_mov_product_created",
            ),
        ]

    def __str__(self) -> str:
        sign = "+" if self.kind == self.MovementKind.IN else "-"
        return f"{sign}{self.quantity} x {self.product}"

    def save(self, *args: object, **kwargs: object) -> None:
        # Tout (vérification + update du produit + insert du mouvement) est atomique :
        # une ValidationError annule aussi bien l'insert que la mise à jour du stock.
        with transaction.atomic():
            product = Product.objects.filter(pk=self.product_id).first()
            if product is None or not product.is_active:
                raise ValidationError(
                    _("Stock movements are not allowed on inactive product %(product)s"),
                    {"product": product.name if product else self.product_id},
                )
            delta = self.quantity if self.kind == self.MovementKind.IN else -self.quantity
            qs = Product.objects.filter(pk=self.product_id)
            if delta < 0:
                # Sortie de stock : on n'incrémente que si la quantité actuelle est
                # suffisante (condition DANS le UPDATE, donc sans course condition).
                # Si aucune ligne n'est mise à jour, c'est que le stock est insuffisant.
                qs = qs.filter(quantity__gte=-delta)
                if not qs.update(quantity=models.F("quantity") + delta):
                    raise ValidationError(
                        _("Insufficient stock for product %(product)s"),
                        {"product": product.name if product else self.product_id},
                    )
            else:
                qs.update(quantity=models.F("quantity") + delta)
            super().save(*args, **kwargs)
