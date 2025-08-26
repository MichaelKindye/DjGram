from django.urls import path
from .views import login_view, home_view, register_view, verify_email_notification_view, verify_email_view

urlpatterns=[
    path('register/', register_view, name='register-page'),
    path('verify-email/', verify_email_notification_view, name='verify-email-message-page'),
    path('verify-email/<str:uidb64>/<str:token>/', verify_email_view, name='verify-email'),
    path('login/', login_view, name='login-page'),
    path('home/', home_view, name='home-page'),
]