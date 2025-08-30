from django.urls import re_path
from .consumers import MessageConsumer, GlobalConsumer

ws_urlpatterns=[
    re_path(r'^ws/$', GlobalConsumer.as_asgi()),
    re_path(r'^ws/(?P<sender>\w+)/(?P<receiver>\w+)/$', MessageConsumer.as_asgi())
]