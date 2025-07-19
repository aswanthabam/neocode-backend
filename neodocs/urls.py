"""
URL configuration for neodocs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
# from oauth2_provider.views import AuthorizationView, TokenView, RevokeTokenView  # Commented out due to import issues
from rest_framework.routers import DefaultRouter
from auth_api.views import (
    UserRegistrationView, UserLoginView, UserProfileView, OrganizationView,
    GoogleOAuthView, TokenRefreshView, LogoutView, PasswordChangeView,
    UserStatsView, NotificationPreferencesView, PrivacySettingsView,
    UserActivityListView
)
from documents.views import (
    DocumentCategoryViewSet, DocumentViewSet, DocumentAccessViewSet,
    DocumentAccessLogViewSet, DocumentShareViewSet, DocumentRequestViewSet,
    DocumentIssueView
)
from sharing.views import (
    QRCodeShareViewSet, ShareSessionViewSet, SharingActivityViewSet,
    DocumentRequestResponseViewSet, ShareNotificationViewSet,
    QRCodeAccessView, ShareStatsView, BulkShareView
)

# Create routers for ViewSets only
router = DefaultRouter()
router.register(r'documents/categories', DocumentCategoryViewSet, basename='document-category')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'documents/access', DocumentAccessViewSet, basename='document-access')
router.register(r'documents/access-logs', DocumentAccessLogViewSet, basename='document-access-log')
router.register(r'sharing/requests', DocumentShareViewSet, basename='document-share')
router.register(r'sharing/requests', DocumentRequestViewSet, basename='document-request')
router.register(r'sharing/qr-shares', QRCodeShareViewSet, basename='qr-share')
router.register(r'sharing/sessions', ShareSessionViewSet, basename='share-session')
router.register(r'sharing/activities', SharingActivityViewSet, basename='sharing-activity')
router.register(r'sharing/responses', DocumentRequestResponseViewSet, basename='document-request-response')
router.register(r'sharing/notifications', ShareNotificationViewSet, basename='share-notification')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation (simplified)
    # path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # path('api/docs/', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    # path('api/redoc/', SpectacularRedocView.as_view(), name='redoc'),
    
    # API v1
    path('api/v1/', include([
        # Authentication endpoints (APIView classes)
        path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
        path('auth/login/', UserLoginView.as_view(), name='user-login'),
        path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
        path('auth/logout/', LogoutView.as_view(), name='user-logout'),
        path('auth/password/change/', PasswordChangeView.as_view(), name='password-change'),
        path('auth/stats/', UserStatsView.as_view(), name='user-stats'),
        path('auth/notifications/preferences/', NotificationPreferencesView.as_view(), name='notification-preferences'),
        path('auth/privacy/settings/', PrivacySettingsView.as_view(), name='privacy-settings'),
        path('auth/activities/', UserActivityListView.as_view(), name='user-activities'),
        
        # Profile and Organization endpoints (APIView classes)
        path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
        path('auth/organization/', OrganizationView.as_view(), name='organization'),
        
        # Google OAuth
        path('auth/google/url/', GoogleOAuthView.as_view(), name='google-oauth-url'),
        path('auth/google/callback/', GoogleOAuthView.as_view(), name='google-oauth-callback'),
        
        # Document management
        path('documents/issue/', DocumentIssueView.as_view(), name='document-issue'),
        
        # Sharing endpoints
        path('sharing/access/', QRCodeAccessView.as_view(), name='qr-access'),
        path('sharing/stats/', ShareStatsView.as_view(), name='share-stats'),
        path('sharing/bulk/', BulkShareView.as_view(), name='bulk-share'),
        
        # Router URLs (ViewSets)
        path('', include(router.urls)),
    ])),
    
    # OAuth2 Provider endpoints (commented out due to import issues)
    # path('o/', include([
    #     path('authorize/', AuthorizationView.as_view(), name='authorize'),
    #     path('token/', TokenView.as_view(), name='token'),
    #     path('revoke_token/', RevokeTokenView.as_view(), name='revoke-token'),
    # ])),
    
    # Legacy API endpoints (for backward compatibility)
    path('api/auth/', include('auth_api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
