import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from core.routing import ws_urlpatterns
from core.auth_middleware import JwtAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjMessage.settings')
django.setup()

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket':JwtAuthMiddleware(
        URLRouter(
            ws_urlpatterns
        )
    )
})
