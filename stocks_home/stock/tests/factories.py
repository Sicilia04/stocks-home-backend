from __future__ import annotations

from factory import Faker
from factory import Sequence
from factory.django import DjangoModelFactory

from stocks_home.stock.models import Product


class ProductFactory(DjangoModelFactory[Product]):
    name = Faker("name")
    barcode = Sequence(lambda n: f"BC-{n:08d}")
    category = "default"
    min = 1
    quantity = 10

    class Meta:
        model = Product
