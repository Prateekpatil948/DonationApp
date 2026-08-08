from django.urls import path

from apps.donations.views import DonationDetailView, DonationListCreateView

app_name = "donations"

urlpatterns = [
    path("", DonationListCreateView.as_view(), name="donation-list"),
    path("<uuid:pk>/", DonationDetailView.as_view(), name="donation-detail"),
]
