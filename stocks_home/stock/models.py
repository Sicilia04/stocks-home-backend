from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    barcode = models.CharField(_("Barcode"), max_length=64, unique=True)
    category = models.CharField(_("Category"), max_length=100)
    min = models.PositiveIntegerField(_("Minimum quantity"), default=0)
    quantity = models.PositiveIntegerField(_("Quantity"), default=0)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self) -> str:
        return self.name
