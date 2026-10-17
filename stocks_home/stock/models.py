"""Domain models for the ``stock`` app.

This module defines the business logic of the stock manager:

* ``Category``        - a product category with a unique auto-generated
  ``slug`` derived from its name.
* ``Product``         - a product identified by a unique barcode
  (EAN-8/EAN-13), belonging to a category and holding a quantity of stock.
* ``StockMovement``   - an auditable stock in/out event. Writing a
  movement atomically updates the product's quantity inside a single
  transaction so either both happen or neither does.

All models extend ``model_utils.models.TimeStampedModel`` and therefore
carry ``created`` / ``modified`` timestamps automatically.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.db import transaction
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

# A barcode must be an EAN-8 (8 digits) or an EAN-13 (13 digits).
barcode_validator = RegexValidator(
    regex=r"^(?:\d{8}|\d{13})$",
    message=_("Barcode must be an EAN-8 or EAN-13 (8 or 13 digits)."),
)


class Category(TimeStampedModel):
    """A product category with a unique name and auto-generated slug.

    The slug is always derived from the name (see ``save``) so categories
    can be addressed by a stable, URL-safe identifier.
    """

    name = models.CharField(_("Name"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        # The slug always follows the name: it is regenerated with ``slugify``
        # on every save. Because ``name`` is unique, the slug is unique too,
        # except when two distinct names slugify to the same string (e.g.
        # "Café" / "cafe"). In that case ``save()`` raises ``IntegrityError``
        # which the API converts into an HTTP 400.
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(TimeStampedModel):
    """A stockable product, identified by a unique barcode.

    A product has a category (``PROTECT`` so a category that still has
    products cannot be deleted), a quantity of stock, a minimum-quantity
    threshold used to flag low stock, and an activation flag.

    The quantity is only ever changed through
    ``StockMovement`` (which keeps an audit trail); it is never written
    directly via the API.
    """

    name = models.CharField(_("Name"), max_length=255)
    barcode = models.CharField(
        _("Barcode"),
        max_length=64,
        unique=True,
        validators=[barcode_validator],
    )
    # PROTECT: deleting a category that still contains products is not allowed.
    category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        on_delete=models.PROTECT,
        related_name="products",
    )
    # Threshold below which the stock is considered low.
    min_quantity = models.PositiveIntegerField(
        _("Minimum quantity"), default=0,
    )
    # Quantity currently in stock; in practice this is only modified by
    # StockMovement (which keeps a trail of every change).
    quantity = models.PositiveIntegerField(_("Quantity"), default=0)
    # An inactive product can no longer receive stock movements.
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def is_low_stock(self) -> bool:
        """``True`` when the quantity is strictly below the minimum threshold."""
        return self.quantity < self.min_quantity


class StockMovement(TimeStampedModel):
    """A stock in/out event that updates the product's quantity.

    Writing the movement and updating the product's quantity happen inside
    the same transaction: if either part fails, the whole operation is
    rolled back.
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
    # The user the movement belongs to (the audit trail is attributed to them).
    # PROTECT: a user that has movements can not be deleted.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )
    kind = models.CharField(_("Kind"), max_length=3, choices=MovementKind.choices)
    # MinValueValidator(1): a movement with a zero quantity is rejected
    # by ``full_clean()``.
    quantity = models.PositiveIntegerField(
        _("Quantity"), validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = _("Stock movement")
        verbose_name_plural = _("Stock movements")
        # "-pk" keeps the ordering stable when timestamps tie.
        ordering = ["-created", "-pk"]
        # Index to speed up "movements of a product, ordered by date" queries.
        indexes = [
            models.Index(
                fields=["product", "created"], name="stock_mov_product_created",
            ),
        ]

    def __str__(self) -> str:
        sign = "+" if self.kind == self.MovementKind.IN else "-"
        return f"{sign}{self.quantity} x {self.product}"

    def save(self, *args: object, **kwargs: object) -> None:
        # Everything (checks + product update + movement insert) is atomic:
        # a ``ValidationError`` rolls back both the insert and the stock update.
        with transaction.atomic():
            product = Product.objects.filter(pk=self.product_id).first()
            if product is None or not product.is_active:
                raise ValidationError(
                    _(
                        "Stock movements are not allowed on "
                        "inactive product %(product)s",
                    ),
                    {"product": product.name if product else self.product_id},
                )
            if self.kind == self.MovementKind.IN:
                delta = self.quantity
            else:
                delta = -self.quantity
            qs = Product.objects.filter(pk=self.product_id)
            if delta < 0:
                # Stock out: only decrement if the current quantity is high
                # enough. The condition lives INSIDE the ``UPDATE`` statement
                # (``quantity__gte=...``), so it is safe against race
                # conditions. If no row is updated, the stock is insufficient.
                qs = qs.filter(quantity__gte=-delta)
                if not qs.update(quantity=models.F("quantity") + delta):
                    raise ValidationError(
                        _("Insufficient stock for product %(product)s"),
                        {"product": product.name if product else self.product_id},
                    )
            else:
                qs.update(quantity=models.F("quantity") + delta)
            super().save(*args, **kwargs)
