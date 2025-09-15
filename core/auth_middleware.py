from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import parse_qs
import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async

User = get_user_model()

class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope.get('query_string', b'').decode())
        token = query_string.get('token')
        token = token[0] if token else None

        if not token and 'header' in scope:
            headers = dict(scope['headers'])
            auth_header = headers.get(b'authorization', None)
            if auth_header:
                try:
                    token = auth_header.decode().split(' ')[1]
                except Exception:
                    token = None

        if token:
            try:
                verified_token = AccessToken(token)
                scope['user'] = await database_sync_to_async(User.objects.get)(pk=verified_token['user_id'])
            except Exception:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)


