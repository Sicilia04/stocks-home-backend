"""Django ``AppConfig`` for the ``users`` app.

Registered in ``config.settings.base.INSTALLED_APPS`` as
``"stocks_home.users.apps.UsersConfig"`` (see ``default_app_config``
convention via ``AppConfig`` default lookup in Django 3.2+).
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    """``AppConfig`` that labels the ``users`` app in the admin and docs."""

    name = "stocks_home.users"
    verbose_name = _("Users")

    def ready(self):
        """Hook run when Django has started the app registry.

        Override in a subclass if you need to connect signals or register
        custom admin actions at startup.
        """
