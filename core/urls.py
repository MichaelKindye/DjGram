from django.urls import path
from .views import login_view,home_view, register_view, verify_email_view, logout_view, fetch_users, get_online_users
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns=[
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register_view, name='register-page'),
    path('verify-email/<str:uidb64>/<str:token>/', verify_email_view, name='verify-email'),
    path('login/', login_view, name='login-page'),
    path('logout/', logout_view, name='logout'),
    path('home/', home_view, name='home-page'),
    path('users/', fetch_users, name='fetch-users'),
    path('status/users/online/', get_online_users, name='get-online-users'),
]