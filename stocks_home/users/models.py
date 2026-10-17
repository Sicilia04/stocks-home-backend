"""User model and app-level user logic for Stocks Home.

The application uses a custom ``User`` model (sub-classing
``AbstractUser``) rather than the default Django user. This is the
recommended approach for new projects: you can safely add custom fields
later without a costly rewrite of ``AUTH_USER_MODEL``.
"""

from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class User(AbstractUser):
    """Default custom user model for Stocks Home.

    Behaves identically to the built-in ``AbstractUser``. If you add fields
    that must be captured at signup time, update
    ``stocks_home.users.forms.UserSignupForm`` accordingly.
    """

    def get_absolute_url(self) -> str:
        """Get the URL for this user's detail view.

        Returns:
            URL (as a string) for the user detail page.
        """
        return reverse("users:detail", kwargs={"username": self.username})
