"""Central django-ninja API instance and global configuration.

This module wires together the REST API for the whole project:

* authenticates every request via JWT (`ninja_jwt`) and/or session auth;
* registers the default django-ninja-jwt controller (login/refresh/logout);
* translates model-level ``ValidationError`` (raised during ``save()`` etc.)
  into a meaningful HTTP 400 response instead of a 500/traceback;
* mounts the ``users`` and ``stock`` routers under ``/api/``.

The interactive OpenAPI docs are served at ``/api/docs/`` and are restricted
to staff users via ``docs_decorator=staff_member_required``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError as DjangoValidationError
from ninja.security import SessionAuth
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController

if TYPE_CHECKING:
    from django.http import HttpRequest

api = NinjaExtraAPI(
    urls_namespace="api",
    auth=[JWTAuth(), SessionAuth()],
    docs_decorator=staff_member_required,
)
api.register_controllers(NinjaJWTDefaultController)


def _handle_model_validation_error(request: HttpRequest, exc: Exception) -> None:
    """Translate a model ``ValidationError`` into an HTTP 400 response.

    Without this handler, ninja would return a 500 (with a full traceback) for
    this kind of exception. The response body follows the same ``detail``
    format that ninja uses for its own validation errors.

    NB: never re-raise from a ninja exception handler (dispatch is
    ``except Exception -> on_exception``); returning ``None`` leaves the
    default behavior in place.
    """
    assert isinstance(
        exc, DjangoValidationError,
    ), "handler registered on django.core.exceptions.ValidationError"
    return api.create_response(request, {"detail": list(exc.messages)}, status=400)


api.add_exception_handler(DjangoValidationError, _handle_model_validation_error)

api.add_router("/users/", "stocks_home.users.api.views.router")
api.add_router("/stock/", "stocks_home.stock.api.views.router")
