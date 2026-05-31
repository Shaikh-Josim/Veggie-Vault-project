from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path("user/create/", views.CreateUserView.as_view(), name="create-user"),
    path("user/check/", views.CheckUserView.as_view(), name="check-user"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("forget-password/", views.ForgetPasswordView.as_view(), name="forget-password"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("profiles/", views.ListUserProfileView.as_view(), name="list-profiles"),
    path("profile/", views.ManageProfileView.as_view(), name="profile"),
    path("profile/location/update/", views.UpdateLocationView.as_view(), name="profile-location-update"),
    path("profile/locations/", views.ListProfileLocationView.as_view(), name="profile-locations"),
    path("profile/locations/delete/", views.DeleteProfileLocationView.as_view(), name="profile-location-delete"),
    path("profile/locations/create", views.AddProfileLocationView.as_view(), name="profile-location-create"),

]
