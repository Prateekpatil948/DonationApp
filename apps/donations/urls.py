from django.urls import path

from apps.donations.views import CategoryDetailView, CategoryListCreateView

app_name = "categories"

urlpatterns = [
    path("", CategoryListCreateView.as_view(), name="category-list"),
    path("<uuid:pk>/", CategoryDetailView.as_view(), name="category-detail"),
]
