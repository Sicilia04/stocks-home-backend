from __future__ import annotations

from django.db.models import QuerySet
from ninja import Router

from stocks_home.stock.api.schema import ProductSchema
from stocks_home.stock.api.schema import UpdateProductSchema
from stocks_home.stock.models import Product

router = Router(tags=["stock"])


def _get_products_queryset(request) -> QuerySet[Product]:
    return Product.objects.all()


@router.get("/", response=list[ProductSchema])
def list_products(request, category: str | None = None):
    queryset = _get_products_queryset(request)
    if category:
        queryset = queryset.filter(category=category)
    return queryset


@router.post("/", response=ProductSchema, status_code=201)
def create_product(request, data: UpdateProductSchema):
    return Product.objects.create(**data.model_dump(exclude_unset=True))


@router.get("/{pk}/", response=ProductSchema)
def retrieve_product(request, pk: int):
    return Product.objects.get(pk=pk)


@router.patch("/{pk}/", response=ProductSchema)
def update_product(request, pk: int, data: UpdateProductSchema):
    product = Product.objects.get(pk=pk)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    product.full_clean()
    product.save()
    return product


@router.delete("/{pk}/", response=None)
def delete_product(request, pk: int):
    Product.objects.filter(pk=pk).delete()
