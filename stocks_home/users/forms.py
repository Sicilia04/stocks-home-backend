"""Django / django-allauth forms for the ``users`` app.

Three groups of forms live here:

* **Admin forms** (``UserAdminChangeForm``, ``UserAdminCreationForm``) used by
  the Django admin to create/edit ``User`` records;
* **Signup form** (``UserSignupForm``) used by the ``django-allauth``
  account signup flow.

If you add a field to the ``User`` model that should be collected at signup
    time, add it to ``UserSignupForm``.
"""

from allauth.account.forms import SignupForm
from django.contrib.auth import forms as admin_forms
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):
    """Admin form used when **editing** an existing user.

    Overrides the model to use this project's ``stocks_home.users.models.User``.
    """

    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """Admin form used when **creating** a user from the admin.

    Use ``UserSignupForm`` instead if you want to change the public
    user-signup flow.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """Form rendered on the user sign-up screen.

    Default fields (username, email, password) are added automatically by
    ``django-allauth``. Extend ``fields`` / add model fields on ``User`` to
    capture more information at signup time.
    """
