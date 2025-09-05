from django.urls import path
from .views import RegisterUser, VerifyEmail, LoginUser, GoogleLogin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)




urlpatterns = [
  path('register/', RegisterUser.as_view(), name='user_register'),
  path("verify-email/<uid64>/<token>/", VerifyEmail.as_view(), name="email-verification"),
  path('login/', LoginUser.as_view(), name='User_login_with_mail'), # custom login system. later add token to cookies.
  path('google-login/', GoogleLogin.as_view(), name='google_login'),
  path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += [
  path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # login system provided by default returs tokens but not set them to cookies by default
  path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), # token refresh 
]
