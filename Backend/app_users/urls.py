from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path("user/", views.ListUserProfileView.as_view(), name="list-users"),
    path("user/create/", views.CreateUserView.as_view(), name="create-user"),
    path("user/check/", views.CheckUserView.as_view(), name="check-user"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("forget-password/", views.ForgetPasswordView.as_view(), name="forget-password"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("profile/", views.UpdateProfileView.as_view(), name="profile"),

]
