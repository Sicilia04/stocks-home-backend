"""django-ninja (Pydantic) schemas for the ``users`` REST API.

Schemas define the JSON contract for user-related endpoints:

* ``UserSchema``       - **read** shape returned in responses.
* ``UpdateUserSchema`` - **write** shape accepted in request bodies.

Both are generated from the ``stocks_home.users.models.User`` Django
model, so they stay in sync with the database fields automatically.
"""

from ninja import ModelSchema

from stocks_home.users.models import User


class UpdateUserSchema(ModelSchema):
    """Request body schema for updating a user.

    Only exposes the fields a client is allowed to change; everything else
    (``password``, ``is_staff``, ...) is handled by admin or the model itself.
    """

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class UserSchema(ModelSchema):
    """Response schema for a user.

    Exposes every column **except** the sensitive ``password`` field, which is
    explicitly excluded so it is never serialized into a JSON payload.
    """

    class Meta:
        model = User
        exclude = ["password"]
