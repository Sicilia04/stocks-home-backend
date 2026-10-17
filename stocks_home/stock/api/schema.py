"""django-ninja (Pydantic) schemas for the ``stock`` app.

A schema is the declaration of the data shape exchanged by the API:

* **output** (*Read*) schemas are generated from the Django models;
* **input** (*Write*) schemas declare the fields accepted in the JSON
  request body, with Pydantic validation (Django validators declared on the
  models — e.g. the EAN barcode — are picked up as well).
"""

from ninja import ModelSchema

from stocks_home.stock.models import Category
from stocks_home.stock.models import Product
from stocks_home.stock.models import StockMovement

# --- Categories ---------------------------------------------------------------


class CategorySchema(ModelSchema):
    """Output schema: what is returned in the JSON response."""

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class CategoryWriteSchema(ModelSchema):
    """Input schema: request body for creating a category.

    The slug is not supplied by the caller — it is generated automatically
    from the name in ``Category.save`` (``slugify``). Uniqueness is
    enforced by the model (``unique=True``).
    """

    class Meta:
        model = Category
        fields = ["name"]


# --- Products -----------------------------------------------------------------


class ProductSchema(ModelSchema):
    """Output schema for a product."""

    # Category name, flattened for easy reading of the JSON (in addition to
    # the id already present in "category").
    category_name: str

    # ``is_low_stock`` is a model ``@property`` (not a database column): it is
    # declared explicitly so ninja reads it from the object.
    is_low_stock: bool

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            # barcode: the model's RegexValidator (EAN-8/EAN-13) is reused by
            # ninja and also applied on input validation.
            "barcode",
            # ForeignKey exposed as a plain id in the output JSON.
            "category",
            # quantity: read-only via the API; modified by movements only.
            "quantity",
            "min_quantity",
            "is_active",
        ]

    @staticmethod
    def resolve_category_name(obj: Product) -> str:
        """Return the category's display name (flattened in the JSON)."""
        return obj.category.name


class ProductWriteSchema(ModelSchema):
    """Input schema for creating / updating a product.

    NB: ``quantity`` is intentionally absent — it must never be written
    directly; it is only updated by stock movements
    (``StockMovement.save`` handles the atomic update).
    """

    class Meta:
        model = Product
        # "category" is accepted as an integer id (ninja automatically
        # converts ForeignKey <-> id).
        fields = ["name", "barcode", "category", "min_quantity", "is_active"]


# --- Stock movements ----------------------------------------------------------


class StockMovementSchema(ModelSchema):
    """Output schema for a stock movement (audit history)."""

    class Meta:
        model = StockMovement
        # "product" is exposed as an id (FK -> id) in the JSON.
        # "created" comes from TimeStampedModel: the value is produced by
        # Django at save time and is never supplied by the client.
        fields = ["id", "product", "user", "kind", "quantity", "created"]


class StockMovementWriteSchema(ModelSchema):
    """Input schema for recording a stock movement (in/out).

    The business-rule validation (active product, sufficient stock) happens
    in ``StockMovement.save``; the API converts the resulting model
    ``ValidationError`` into an HTTP 400 response (see ``config.api``).
    """

    class Meta:
        model = StockMovement
        # kind: the model's TextChoices -> Pydantic enum "in" / "out".
        # quantity: the model's MinValueValidator(1) is reused by ninja, so
        # 0 and negative numbers are rejected on the API side as well.
        fields = ["product", "kind", "quantity"]
