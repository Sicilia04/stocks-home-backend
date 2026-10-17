"""django-allauth adapter overrides for the ``users`` app.

``AccountAdapter`` customizes the behavior of the ``django-allauth`` account
app (signup, email, etc.) for this project. It is registered via
    ``ACCOUNT_ADAPTER`` in ``config.settings.base``.
"""

from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

if typing.TYPE_CHECKING:
    from django.http import HttpRequest


class AccountAdapter(DefaultAccountAdapter):
    """Project-wide django-allauth adapter.

    Currently only controls whether public self-signup is enabled (useful to
    close registration during an incident or for multi-tenant deployments).
    """

    def is_open_for_signup(self, request: HttpRequest) -> bool:
        """Whether the signup endpoint is currently open.

        Returns:
            ``True`` if ``settings.ACCOUNT_ALLOW_REGISTRATION`` is enabled
            (defaults to ``True`` when the setting is not defined).
        """
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
