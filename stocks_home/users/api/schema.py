from django.urls import reverse
from ninja import ModelSchema

from stocks_home.users.models import User


class UpdateUserSchema(ModelSchema):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", 'email']


class UserSchema(ModelSchema):
    class Meta:
        model = User
        exclude = ['password']
