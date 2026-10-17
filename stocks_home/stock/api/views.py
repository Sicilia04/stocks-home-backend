"""REST API endpoints for the ``stock`` app (django-ninja routes).

Routes are mounted at ``/api/stock/`` via ``config.api``. Every route
requires an authenticated request (enforced globally by the global
``auth=[JWTAuth(), SessionAuth()]`` list in ``config.api``).

Endpoint overview:

* ``/api/stock/categories/``                       - list
* ``POST   /api/stock/categories/``                - create
* ``GET    /api/stock/categories/{id}/``           - fetch one
* ``PATCH  /api/stock/categories/{id}/``           - update
* ``DELETE /api/stock/categories/{id}/``           - delete (refused if it has products)

* ``GET    /api/stock/products/``                  - list
* ``GET    /api/stock/products/{id}/``             - fetch one
* ``POST   /api/stock/products/``                  - create
* ``PATCH  /api/stock/products/{id}/``             - update
* ``DELETE /api/stock/products/{id}/``             - delete (cascades to movements)

* ``GET    /api/stock/movements/``                 - list
* ``GET    /api/stock/movements/{id}/``            - fetch one
* ``POST   /api/stock/movements/``                 - create the movement
                                                       (also updates product stock)
"""

from __future__ import annotations

from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from ninja import Router
from ninja.errors import HttpError

from stocks_home.stock.api.schema import CategorySchema
from stocks_home.stock.api.schema import CategoryWriteSchema
from stocks_home.stock.api.schema import ProductSchema
from stocks_home.stock.api.schema import ProductWriteSchema
from stocks_home.stock.api.schema import StockMovementSchema
from stocks_home.stock.api.schema import StockMovementWriteSchema
from stocks_home.stock.models import Category
from stocks_home.stock.models import Product
from stocks_home.stock.models import StockMovement

router = Router(tags=["stock"])


# --- Categories ---------------------------------------------------------------


@router.get("/categories/", response=list[CategorySchema])
def list_categories(request: HttpRequest) -> list[Category]:
    """``GET /api/stock/categories/`` - list every category."""
    return list(Category.objects.all())


@router.post("/categories/", response=CategorySchema)
def create_category(request: HttpRequest, payload: CategoryWriteSchema) -> Category:
    """``POST /api/stock/categories/`` - create a category.

    The slug is not part of the payload: it is generated from the name
    by ``Category.save`` and is therefore always in sync with the name.
    A duplicate name / slug triggers ``IntegrityError`` from the database,
    which surfaces as an HTTP 500 (a raw database error, not a business
    rule). Use an existing unique name to avoid this.
    """
    return Category.objects.create(**payload.model_dump())


@router.delete("/categories/{category_id}/")
def delete_category(request: HttpRequest, category_id: int) -> HttpResponse:
    """``DELETE /api/stock/categories/{id}/`` - delete a category.

    Returns HTTP 409 if the category still has products (``on_delete=PROTECT``)
    and HTTP 204 on success.
    """
    category = get_object_or_404(Category, pk=category_id)
    try:
        category.delete()
    except ProtectedError as exc:
        # The category still has products -> not allowed (on_delete=PROTECT).
        raise HttpError(
            409,
            _("A category with products can not be deleted."),
        ) from exc
    return HttpResponse(status=204)


@router.patch("/categories/{category_id}/", response=CategorySchema)
def update_category(
    request: HttpRequest, category_id: int, payload: CategoryWriteSchema,
) -> Category:
    """``PATCH /api/stock/categories/{id}/`` - update a category name.

    The slug is recomputed automatically by ``Category.save`` (``slugify``).
    If the new name is already taken by another category, the database raises
    ``IntegrityError`` (``unique=True``) which is returned as HTTP 400.
    """
    # Unknown pk -> 404 (``Http404`` is handled by ninja).
    category = get_object_or_404(Category, pk=category_id)
    category.name = payload.name
    # NB: the slug is recomputed automatically by ``Category.save`` (``slugify``).
    # Name already taken by another category -> ``IntegrityError`` (``unique=True``).
    try:
        category.save()
    except IntegrityError as exc:
        raise HttpError(
            400,
            _("A category with this name already exists."),
        ) from exc
    return category


@router.get("/categories/{category_id}/", response=CategorySchema)
def get_category(request: HttpRequest, category_id: int) -> Category:
    """``GET /api/stock/categories/{id}/`` - fetch a single category.

    404 when the category does not exist.
    """
    # Unknown pk -> 404 (``Http404`` is handled by ninja).
    return get_object_or_404(Category, pk=category_id)


# --- Products -----------------------------------------------------------------


@router.get("/products/", response=list[ProductSchema])
def list_products(request: HttpRequest) -> list[Product]:
    """``GET /api/stock/products/`` - list every product."""
    return list(Product.objects.all())


@router.get("/products/{product_id}/", response=ProductSchema)
def get_product(request: HttpRequest, product_id: int) -> Product:
    """``GET /api/stock/products/{id}/`` - fetch a single product.

    404 when the product does not exist.
    """
    # Unknown pk -> 404 (``Http404`` is handled by ninja).
    return get_object_or_404(Product, pk=product_id)


@router.post("/products/", response=ProductSchema)
def create_product(request: HttpRequest, payload: ProductWriteSchema) -> Product:
    """``POST /api/stock/products/`` - create a product.

    ``category`` in the payload is the primary-key (id) of the related
    category: ninja converts between the FK and its id automatically, but
    Django only accepts a raw pk on the *attname* ``category_id`` (on
    ``category`` itself it expects a ``Category`` instance).
    """
    # payload["category"] is the FK primary key (ninja converts FK -> id) ;
    # Django only accepts a raw pk on the attname "category_id"
    # (on "category" itself it expects a ``Category`` instance).
    data = payload.model_dump()
    if (category_id := data.pop("category", None)) is not None:
        data["category_id"] = category_id
    return Product.objects.create(**data)


@router.patch("/products/{product_id}/", response=ProductSchema)
def update_product(
    request: HttpRequest, product_id: int, payload: ProductWriteSchema,
) -> Product:
    """``PATCH /api/stock/products/{id}/`` - update a product.

    ``quantity`` is intentionally not updateable from the API - it is only
    modified by stock movements (see ``StockMovement.save``).
    """
    # Unknown pk -> 404 (``Http404`` is handled by ninja).
    product = get_object_or_404(Product, pk=product_id)
    # FK -> attname ``category_id`` (same rules as ``create_product``).
    data = payload.model_dump()
    if (category_id := data.pop("category", None)) is not None:
        data["category_id"] = category_id
    # "quantity" is never written via the API: only movements update it.
    for field, value in data.items():
        setattr(product, field, value)
    product.save()
    return product


@router.delete("/products/{product_id}/")
def delete_product(request: HttpRequest, product_id: int) -> HttpResponse:
    """``DELETE /api/stock/products/{id}/`` - delete a product.

    The product's stock movements are also deleted (``CASCADE`` declared on
    ``StockMovement.product``): the audit trail goes with the product.
    """
    product = get_object_or_404(Product, pk=product_id)
    # NB: the product's stock movements are also deleted (``CASCADE``
    # declared on ``StockMovement.product``): the audit trail goes with it.
    product.delete()
    return HttpResponse(status=204)


# --- Stock movements ----------------------------------------------------------


@router.get("/movements/", response=list[StockMovementSchema])
def list_movements(request: HttpRequest) -> list[StockMovement]:
    """``GET /api/stock/movements/`` - list every stock movement."""
    return list(StockMovement.objects.all())


@router.post("/movements/", response=StockMovementSchema)
def create_movement(
    request: HttpRequest, payload: StockMovementWriteSchema,
) -> StockMovement:
    """``POST /api/stock/movements/`` - record a stock in/out event.

    ``user`` is never supplied by the client: it is always the signed-in
    user (set from ``request.user``).

    ``product`` in the payload is the product's id; it is converted to the
    attname ``product_id`` before hitting the model.

    Business rules (active product, sufficient stock) are enforced by
    ``StockMovement.save``; the resulting model ``ValidationError`` is
    translated into an HTTP 400 by the handler in ``config.api``.
    """
    # product is the FK primary key -> attname ``product_id`` (Django expects
    # an instance on ``product``).
    data = payload.model_dump()
    if (product_id := data.pop("product", None)) is not None:
        data["product_id"] = product_id
    # user is never supplied by the client: it is the signed-in user.
    data["user"] = request.user
    return StockMovement.objects.create(**data)


@router.get("/movements/{movement_id}/", response=StockMovementSchema)
def get_movement(request: HttpRequest, movement_id: int) -> StockMovement:
    """``GET /api/stock/movements/{id}/`` - fetch a single stock movement.

    404 when the movement does not exist.
    """
    # Unknown pk -> 404 (``Http404`` is handled by ninja).
    return get_object_or_404(StockMovement, pk=movement_id)
