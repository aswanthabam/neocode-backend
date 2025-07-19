from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    GoogleOAuthView,
    TokenRefreshView,
    LogoutView
)

app_name = 'auth_api'

urlpatterns = [
    # Registration and Login
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Google OAuth
    path('google/', GoogleOAuthView.as_view(), name='google_oauth'),
    path('google/url/', GoogleOAuthView.as_view(), name='google_oauth_url'),
    
    # Token Management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] 