from ninja import ModelSchema

from stocks_home.stock.models import Product


class ProductSchema(ModelSchema):
    class Meta:
        model = Product
        fields = "__all__"


class UpdateProductSchema(ModelSchema):
    class Meta:
        model = Product
        fields = {
            "name": ["write_only"],
            "barcode": ["write_only"],
            "category": ["write_only"],
            "min": ["write_only"],
            "quantity": ["write_only"],
        }
