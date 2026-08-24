from __future__ import annotations

from django.urls import resolve
from django.urls import reverse


def test_product_list():
    assert reverse("api:list_products") == "/api/stock/"
    assert resolve("/api/stock/").view_name == "api:list_products"


def test_product_detail():
    assert reverse("api:retrieve_product", kwargs={"pk": 1}) == "/api/stock/1/"
    assert resolve("/api/stock/1/").view_name == "api:retrieve_product"
