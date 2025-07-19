from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    UserProfileView,
    GoogleOAuthView,
    RefreshTokenView,
    LogoutView,
    google_oauth_url
)

app_name = 'auth_api'

urlpatterns = [
    # Registration and Login
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Google OAuth
    path('google/', GoogleOAuthView.as_view(), name='google_oauth'),
    path('google/url/', google_oauth_url, name='google_oauth_url'),
    
    # Token Management
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
] 