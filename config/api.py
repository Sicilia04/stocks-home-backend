from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import HttpRequest
from ninja.security import SessionAuth
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController

api = NinjaExtraAPI(
    urls_namespace="api",
    auth=[JWTAuth(), SessionAuth()],
    docs_decorator=staff_member_required,
)
api.register_controllers(NinjaJWTDefaultController)


def _handle_model_validation_error(request: HttpRequest, exc: Exception) -> None:
    """Convertit la ValidationError levée dans un modele (save, etc.) en 400.

    Sans ce handler, ninja renvoie une 500/traceback pour ce genre d'exception.
    Le corps renvoye suit le meme format "detail" que les erreurs de validation
    de ninja. NB : ne jamais re-raise dans un handler ninja (le dispatch est
    except Exception -> on_exception) : retourner None laisse le default.
    """
    assert isinstance(
        exc, DjangoValidationError
    ), "handler enregistre sur django.core.exceptions.ValidationError"
    return api.create_response(request, {"detail": list(exc.messages)}, status=500)


api.add_exception_handler(DjangoValidationError, _handle_model_validation_error)

api.add_router("/users/", "stocks_home.users.api.views.router")
api.add_router("/stock/", "stocks_home.stock.api.views.router")
