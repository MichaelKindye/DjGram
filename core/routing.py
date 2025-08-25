from django.urls import re_path
from .consumers import MessageConsumer

ws_urlpatterns=[
    re_path(r'ws/', MessageConsumer.as_asgi())
]