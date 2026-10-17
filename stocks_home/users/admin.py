"""Django admin configuration for the ``users`` app.

Registers a dedicated ``UserAdmin`` (inheriting from
``django.contrib.auth``'s ``UserAdmin``) that uses the project's custom
forms and displays the same field groups as the default user admin.

When ``settings.DJANGO_ADMIN_FORCE_ALLAUTH`` is true, the admin login page
is replaced by the ``django-allauth`` signup/login flow so that every
session in the project goes through a single, consistent authentication
path.
"""

from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the admin sign-in process to go through the ``django-allauth``
    # workflow (so it shares the same auth pipeline as the rest of the app):
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    """Admin class for ``stocks_home.users.models.User``.

    Re-uses the stock ``UserAdmin`` layout but swaps in the project's custom
    creation/change forms (so the right model is used) and trims the field
    sets to the user fields that matter in this app.
    """

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("email", "last_name", "first_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "last_name", "first_name", "is_superuser"]
    search_fields = ["username", "last_name", "first_name"]
