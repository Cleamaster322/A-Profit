from urllib.parse import unquote

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken


@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user_id = access_token.get("user_id")
        user = get_user_model().objects.get(pk=user_id)
        return user if user.is_active else None
    except (InvalidToken, TokenError, TypeError, ValueError, get_user_model().DoesNotExist):
        return None


class JwtAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        token = self._get_token(scope)
        scope["user"] = await get_user_from_token(token) if token else None
        return await self.app(scope, receive, send)

    @staticmethod
    def _get_token(scope):
        for protocol in scope.get("subprotocols", []):
            if protocol != "jwt":
                return unquote(protocol)
        return None


def JwtAuthMiddlewareStack(app):
    return JwtAuthMiddleware(app)
