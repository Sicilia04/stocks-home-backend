"""REST API endpoints for the ``users`` app (django-ninja routes).

Routes are mounted at ``/api/users/`` via ``config.api``.
Every route requires an authenticated request (enforced globally by the
global ``auth=[JWTAuth(), SessionAuth()]`` list in
``config.api``).

``_get_users_queryset`` scopes every read/write to the *currently signed-in*
user — a caller can only see or modify their own record.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from ninja import Router

from stocks_home.users.api.schema import UpdateUserSchema
from stocks_home.users.api.schema import UserSchema
from stocks_home.users.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest

router = Router(tags=["users"])


def _get_users_queryset(request: HttpRequest) -> QuerySet[User]:
    """Return a queryset scoped to the signed-in user only.

    This is the single source of truth for permission checks in this router:
    every other route funnels through it so no other record can be read or
    written by an unauthenticated / different user.

    Args:
        request: authenticated Django request (guaranteed by the API-level
            auth middleware).

    Returns:
        A ``QuerySet[User]`` containing at most the signed-in user.
    """
    return User.objects.filter(pk=request.user.pk)


@router.get("/", response=list[UserSchema])
def list_users(request: HttpRequest) -> list[User]:
    """``GET /api/users/`` — list the signed-in user (self only)."""
    return list(_get_users_queryset(request))


@router.get("/me/", response=UserSchema)
def retrieve_current_user(request: HttpRequest) -> User:
    """``GET /api/users/me/`` — fetch the signed-in user."""
    return request.user


@router.get("/{username}/", response=UserSchema)
def retrieve_user(request: HttpRequest, username: str) -> User:
    """``GET /api/users/{username}/`` — fetch a user by username.

    404 if the username does not exist **or** belongs to another account
    (the queryset is scoped to ``request.user``).
    """
    users_qs = _get_users_queryset(request)
    return get_object_or_404(users_qs, username=username)


@router.patch("/me/", response=UserSchema)
def update_current_user(request: HttpRequest, data: UpdateUserSchema) -> User:
    """``PATCH /api/users/me/`` — update the signed-in user's profile."""
    user = request.user
    user.name = data.name
    user.username = data.username
    user.save()
    return user


@router.patch("/{username}/", response=UserSchema)
def update_user(
    request: HttpRequest, username: str, data: UpdateUserSchema,
) -> User:
    """``PATCH /api/users/{username}/`` — update a user by username.

    Same scoping as ``retrieve_user``: only the signed-in user can be
    modified.
    """
    users_qs = _get_users_queryset(request)
    user = get_object_or_404(users_qs, username=username)
    user.name = data.name
    user.username = data.username
    user.save()
    return user
