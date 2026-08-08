from django.urls import path

from apps.common.views import TempleSettingsView

app_name = "common"

urlpatterns = [
    path("", TempleSettingsView.as_view(), name="temple-settings"),
]
