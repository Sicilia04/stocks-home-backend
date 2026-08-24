from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stocks_home.stock.models import Product


def test_product_str(product: Product):
    assert str(product) == product.name
