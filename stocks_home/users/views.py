"""Class-based views for the ``users`` app (Django server-rendered views).

These views are the template/UI side of user management (view profile, edit
profile, redirect to profile). They are wired to URL patterns in
``stocks_home.users.urls`` and require an authenticated session
(``LoginRequiredMixin``).

The REST/JSON API for users lives separately in
``stocks_home.users.api.views``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from stocks_home.users.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet


class UserDetailView(LoginRequiredMixin, DetailView):
    """Display the profile of an authenticated user.

    Looks the user up by ``username`` (``slug_field``) so the URL is stable
    and human-readable rather than a raw primary key.
    """

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edit the *currently signed-in* user's profile.

    ``get_object`` always returns ``request.user`` (so a user can only edit
    their own record), and on success the view shows a success message and
    redirects back to the profile detail page.

    ``assert ... is_authenticated`` is used as a mypy "type guard": the mixin
    already guarantees authentication at runtime, so the assert is only there
    to narrow the type for the type checker.
    """

    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    """Redirect to the profile of the currently signed-in user."""

    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()
