from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from stocks_home.stock.tests.factories import ProductFactory
from stocks_home.users.tests.factories import UserFactory

if TYPE_CHECKING:
    from django.test import Client

    from stocks_home.stock.models import Product
    from stocks_home.users.models import User

pytestmark = pytest.mark.django_db


def _product_dict(product: Product) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "barcode": product.barcode,
        "category": product.category,
        "min": product.min,
        "quantity": product.quantity,
    }


def test_list_products_as_anonymous_user(client: Client):
    response = client.get(reverse("api:list_products"))
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_list_products(client: Client, user: User, product: Product):
    client.force_login(user)
    ProductFactory.create(category="other")
    response = client.get(reverse("api:list_products"))
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 2


def test_list_products_by_category(client: Client, user: User, product: Product):
    client.force_login(user)
    response = client.get(
        reverse("api:list_products"), params={"category": "other"},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_retrieve_product(client: Client, user: User, product: Product):
    client.force_login(user)
    response = client.get(
        reverse("api:retrieve_product", kwargs={"pk": product.pk}),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == _product_dict(product)


def test_create_product(client: Client, user: User):
    client.force_login(user)
    response = client.post(
        reverse("api:create_product"),
        data='{"name": "Cola", "barcode": "123", "category": "boisson", "min": 2, "quantity": 10}',
        content_type="application/json",
    )
    assert response.status_code == HTTPStatus.CREATED, response.json()
    body = response.json()
    assert body["name"] == "Cola"
    assert body["barcode"] == "123"
    assert ProductFactory.Meta.model.objects.filter(barcode="123").count() == 1


def test_update_product(client: Client, user: User, product: Product):
    client.force_login(user)
    response = client.patch(
        reverse("api:update_product", kwargs={"pk": product.pk}),
        data='{"name": "New Name"}',
        content_type="application/json",
    )
    assert response.status_code == HTTPStatus.OK, response.json()
    assert response.json()["name"] == "New Name"
    product.refresh_from_db()
    assert product.name == "New Name"


def test_delete_product(client: Client, user: User, product: Product):
    client.force_login(user)
    response = client.delete(
        reverse("api:delete_product", kwargs={"pk": product.pk}),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
