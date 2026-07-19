from django.urls import path

from apps.authentication.views import GoogleLoginView, LogoutView, TokenRefreshView

app_name = "authentication"

urlpatterns = [
    path("google/login", GoogleLoginView.as_view(), name="google-login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("refresh", TokenRefreshView.as_view(), name="refresh"),
]
