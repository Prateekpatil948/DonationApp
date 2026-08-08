from django.urls import path

from apps.users.member_views import (
    DeactivateMemberView,
    InviteMemberView,
    MemberDetailView,
    MemberListView,
    ReactivateMemberView,
    SuspendMemberView,
)

app_name = "members"

urlpatterns = [
    path("invite", InviteMemberView.as_view(), name="invite"),
    path("", MemberListView.as_view(), name="list"),
    path("<uuid:pk>/", MemberDetailView.as_view(), name="detail"),
    path("<uuid:pk>/suspend", SuspendMemberView.as_view(), name="suspend"),
    path("<uuid:pk>/reactivate", ReactivateMemberView.as_view(), name="reactivate"),
    path("<uuid:pk>/deactivate", DeactivateMemberView.as_view(), name="deactivate"),
]
