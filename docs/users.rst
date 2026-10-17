.. _users:

Users
======================================================================

Stocks Home uses a **custom user model** instead of Django's default ``User``.
Even when the default model would be sufficient, defining your own is strongly
recommended: it is the only way to add fields later without a risky,
schema-migration on an already-deployed ``AUTH_USER_MODEL``.

The model in :class:`stocks_home.users.models.User` currently behaves exactly
like the built-in ``AbstractUser``. If you add a field that must be captured
at signup, remember to also expose it in
``stocks_home.users.forms.UserSignupForm``.

The module is auto-documented below.

.. automodule:: stocks_home.users.models
   :members:
   :undoc-members:
   :show-inheritance:
