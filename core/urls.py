from django.urls import path
from .views import login_view, home_view, register_view

urlpatterns=[
    path('register/', register_view, name='register-page'),
    path('login/', login_view, name='login-page'),
    path('home/', home_view, name='home-page'),
]