"""Schemas django-ninja pour l'application stock.

Un schema est la declaration du format de donnee echange par l'API :
- les schemas de sortie (Read) sont generes a partir des modeles Django ;
- les schemas d'entree (Write) definissent les champs acceptes dans le
  corps de requete JSON, avec validation Pydantic (les validateurs Django
  declares sur les modeles, comme le code-barres EAN, sont reperes aussi).
"""

from ninja import ModelSchema

from stocks_home.stock.models import Category
from stocks_home.stock.models import Product
from stocks_home.stock.models import StockMovement


# --- Categories ---------------------------------------------------------------


class CategorySchema(ModelSchema):
    """Schema de sortie : ce qui est renvoye dans les reponses JSON."""

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class CategoryWriteSchema(ModelSchema):
    """Schema d'entree : corps de requete pour creer une categorie.

    Le slug n'est pas fourni par l'appelant : il est genere automatiquement
    depuis le nom dans Category.save() (slugify).
    L'unicite est garantie par le modele (unique=True).
    """

    class Meta:
        model = Category
        fields = ["name"]


# --- Produits -----------------------------------------------------------------


class ProductSchema(ModelSchema):
    """Schema de sortie pour un produit."""
    # Nom de la categorie, expose a plat pour une lecture facile du JSON
    # (en plus de l'id deja presente dans "category").
    category_name: str

    # is_low_stock est une @property du modele (pas une colonne de base de
    # donnees) : declaree explicitement, ninja la lit sur l'objet.
    is_low_stock: bool

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            # barcode : le RegexValidator du modele (EAN-8/EAN-13) est
            # repris par ninja et applique aussi a la validation d'entree.
            "barcode",
            # ForeignKey exposee comme un simple id dans le JSON de sortie.
            "category",
            # quantity : lecture seule via l'API, modifiee par les mouvements.
            "quantity",
            "min_quantity",
            "is_active",
        ]

    @staticmethod
    def resolve_category_name(obj: Product) -> str:
        return obj.category.name


class ProductWriteSchema(ModelSchema):
    """Schema d'entree pour creer/mettre a jour un produit.

    NB : quantity est volontairement absente : elle ne doit jamais etre
    ecrite directement, uniquement mise a jour par les mouvements de stock
    (StockMovement.save() gere la mise a jour atomique).
    """
    class Meta:
        model = Product
        # "category" est acceptee sous forme d'id entier (ninja convertit
        # automatiquement les ForeignKey en id et inversement).
        fields = ["name", "barcode", "category", "min_quantity", "is_active"]


# --- Mouvements de stock --------------------------------------------------------


class StockMovementSchema(ModelSchema):
    """Schema de sortie pour un mouvement (historique)."""

    class Meta:
        model = StockMovement
        # "product" est expose comme un id (FK -> id) dans le JSON.
        # "created" vient de TimeStampedModel : la valeur est produite
        # par Django a l'enregistrement, jamais fournie par le client.
        fields = ["id", "product", "user", "kind", "quantity", "created"]


class StockMovementWriteSchema(ModelSchema):
    """Schema d'entree pour enregistrer un mouvement (entree/sortie).

    La validation des regles de gestion (produit actif, stock suffisant)
    se fait dans StockMovement.save() ; l'API convertit la ValidationError
    du modele en reponse HTTP 400.
    """

    class Meta:
        model = StockMovement
        # kind : TextChoices du modele -> enum Pydantic "in" / "out".
        # quantity : le MinValueValidator(1) du modele est repris par ninja,
        # on refuse donc 0 et les nombres negatifs des cote API aussi.
        fields = ["product", "kind", "quantity"]
