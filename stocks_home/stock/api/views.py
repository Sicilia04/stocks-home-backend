from __future__ import annotations

from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
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


@router.get("/categories/", response=list[CategorySchema])
def list_categories(request):
    return Category.objects.all()


@router.post("/categories/", response=CategorySchema)
def create_category(request, payload: CategoryWriteSchema):
    return Category.objects.create(**payload.model_dump())


@router.delete("/categories/{category_id}/")
def delete_category(request, category_id: int):
    category = get_object_or_404(Category, pk=category_id)
    try:
        category.delete()
    except ProtectedError:
        # La categorie a des produits -> impossible (on_delete=PROTECT).
        raise HttpError(
            409,
            _("A category with products can not be deleted."),
        )
    return HttpResponse(status=204)


@router.patch("/categories/{category_id}/", response=CategorySchema)
def update_category(request, category_id: int, payload: CategoryWriteSchema):
    # pk inconnu -> 404 (Http404 est gere par ninja).
    category = get_object_or_404(Category, pk=category_id)
    category.name = payload.name
    # NB : le slug est recalcule automatiquement par Category.save() (slugify).
    # Nom deja pris par une autre categorie -> IntegrityError (unique=True).
    try:
        category.save()
    except IntegrityError:
        raise HttpError(
            400,
            _("A category with this name already exists."),
        )
    return category


@router.get("/categories/{category_id}/", response=CategorySchema)
def get_category(request, category_id: int):
    # pk inconnu -> 404 (Http404 est gere par ninja).
    return get_object_or_404(Category, pk=category_id)


@router.get("/products/", response=list[ProductSchema])
def list_products(request):
    return Product.objects.all()


@router.get("/products/{product_id}/", response=ProductSchema)
def get_product(request, product_id: int):
    # pk inconnu -> 404 (Http404 est gere par ninja).
    return get_object_or_404(Product, pk=product_id)


@router.post("/products/", response=ProductSchema)
def create_product(request, payload: ProductWriteSchema):
    # payload["category"] est le pk de la FK (ninja convertit FK -> id) ;
    # Django n'accepte un pk brut que sur l'attname "category_id"
    # (sur "category" il faut une instance Category).
    data = payload.model_dump()
    if (category_id := data.pop("category", None)) is not None:
        data["category_id"] = category_id
    return Product.objects.create(**data)


@router.patch("/products/{product_id}/", response=ProductSchema)
def update_product(request, product_id: int, payload: ProductWriteSchema):
    # pk inconnu -> 404 (Http404 est gere par ninja).
    product = get_object_or_404(Product, pk=product_id)
    # FK -> attname "category_id" (memes regles que create_product).
    data = payload.model_dump()
    if (category_id := data.pop("category", None)) is not None:
        data["category_id"] = category_id
    # "quantity" n'est jamais ecrite via l'API : uniquement par les mouvements.
    for field, value in data.items():
        setattr(product, field, value)
    product.save()
    return product


@router.delete("/products/{product_id}/")
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, pk=product_id)
    # NB : les mouvements de stock du produit sont aussi supprimes (CASCADE
    # declaree sur StockMovement.product) : l'historique part avec lui.
    product.delete()
    return HttpResponse(status=204)


@router.get("/movements/", response=list[StockMovementSchema])
def list_movements(request):
    return StockMovement.objects.all()


@router.post("/movements/", response=StockMovementSchema)
def create_movement(request, payload: StockMovementWriteSchema):
    # product est le pk de la FK -> attname "product_id" (Django exige une
    # instance sur "product").
    data = payload.model_dump()
    if (product_id := data.pop("product", None)) is not None:
        data["product_id"] = product_id
    # user n'est jamais fourni par le client : c'est l'utilisateur connecte.
    data["user"] = request.user
    return StockMovement.objects.create(**data)


@router.get("/movements/{movement_id}/", response=StockMovementSchema)
def get_movement(request, movement_id: int):
    # pk inconnu -> 404 (Http404 est gere par ninja).
    return get_object_or_404(StockMovement, pk=movement_id)
