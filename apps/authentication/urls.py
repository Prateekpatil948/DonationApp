from django.urls import path

from apps.authentication.views import (
    ChangePinView,
    LoginView,
    LogoutView,
    SignupView,
    TokenRefreshView,
)

app_name = "authentication"

urlpatterns = [
    path("signup", SignupView.as_view(), name="signup"),
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("refresh", TokenRefreshView.as_view(), name="refresh"),
    path("change-pin", ChangePinView.as_view(), name="change-pin"),
]
