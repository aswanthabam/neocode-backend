from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import (
    CustomUser,
    Organization,
    OAuthToken,
    UserActivity,
    UserSecuritySettings,
)
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    OrganizationSerializer,
    OrganizationCreateSerializer,
    OrganizationUpdateSerializer,
    GoogleOAuthSerializer,
    OAuthTokenSerializer,
    UserActivitySerializer,
    TokenRefreshSerializer,
    LogoutSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    UserStatsSerializer,
    NotificationPreferencesSerializer,
    PrivacySettingsSerializer,
    UserSecuritySettingsSerializer,
    SecuritySettingsUpdateSerializer,
    PINVerificationSerializer,
)
from documents.models import Document, DocumentShare, DocumentRequest


class UserRegistrationView(APIView):
    """User registration endpoint"""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Register new user",
        description="Create a new user account with email and password",
        request=UserRegistrationSerializer,
        responses={201: UserRegistrationSerializer, 400: "Bad Request"},
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type="registration",
                description=f"User registered with email {user.email}",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            return Response(
                {
                    "message": "User registered successfully",
                    "user": UserProfileSerializer(user).data,
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class UserLoginView(APIView):
    """User login endpoint"""

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="User login",
        description="Authenticate user with email and password",
        request=UserLoginSerializer,
        responses={200: "Login successful", 400: "Invalid credentials"},
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Update last login
            user.last_login = timezone.now()
            user.save()

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type="login",
                description=f"User logged in from {self.get_client_ip(request)}",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            return Response(
                {
                    "message": "Login successful",
                    "user": UserProfileSerializer(user).data,
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class UserProfileView(APIView):
    """User profile management"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get user profile",
        description="Retrieve current user's profile information",
        responses={200: UserProfileSerializer},
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update user profile",
        description="Update current user's profile details",
        request=UserProfileUpdateSerializer,
        responses={200: UserProfileSerializer, 400: "Bad Request"},
    )
    def put(self, request):
        serializer = UserProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()

            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type="profile_updated",
                description="User updated profile information",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            return Response(UserProfileSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class OrganizationView(APIView):
    """Organization profile management"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get organization profile",
        description="Retrieve organization profile information",
        responses={200: OrganizationSerializer, 404: "Organization not found"},
    )
    def get(self, request):
        try:
            organization = Organization.objects.get(user=request.user)
            serializer = OrganizationSerializer(organization)
            return Response(serializer.data)
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(
        summary="Create organization profile",
        description="Create organization profile for issuer/requester users",
        request=OrganizationCreateSerializer,
        responses={201: OrganizationSerializer, 400: "Bad Request"},
    )
    def post(self, request):
        # Check if organization already exists
        if Organization.objects.filter(user=request.user).exists():
            return Response(
                {"error": "Organization profile already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OrganizationCreateSerializer(data=request.data)
        if serializer.is_valid():
            organization = serializer.save()

            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type="organization_created",
                description=f"Created organization profile: {organization.name}",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            return Response(
                OrganizationSerializer(organization).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update organization profile",
        description="Update organization profile details",
        request=OrganizationUpdateSerializer,
        responses={
            200: OrganizationSerializer,
            400: "Bad Request",
            404: "Organization not found",
        },
    )
    def put(self, request):
        try:
            organization = Organization.objects.get(user=request.user)
            serializer = OrganizationUpdateSerializer(
                organization, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()

                # Log activity
                UserActivity.objects.create(
                    user=request.user,
                    activity_type="organization_updated",
                    description=f"Updated organization profile: {organization.name}",
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                )

                return Response(OrganizationSerializer(organization).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class GoogleOAuthView(APIView):
    """Google OAuth authentication"""

    @extend_schema(
        summary="Google OAuth URL",
        description="Get Google OAuth authorization URL",
        responses={200: "OAuth URL"},
    )
    def get(self, request):
        # This would typically redirect to Google OAuth
        # For now, return a placeholder URL
        return Response(
            {
                "auth_url": "https://accounts.google.com/oauth/authorize?client_id=your-client-id&redirect_uri=your-redirect-uri&scope=email profile&response_type=code"
            }
        )

    @extend_schema(
        summary="Google OAuth callback",
        description="Handle Google OAuth callback and create/authenticate user",
        request=GoogleOAuthSerializer,
        responses={200: "OAuth successful", 400: "OAuth failed"},
    )
    def post(self, request):
        serializer = GoogleOAuthSerializer(data=request.data)
        if serializer.is_valid():
            # Here you would validate the Google access token
            # and create/authenticate the user
            # For now, return a placeholder response
            return Response({"message": "Google OAuth successful"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    """Token refresh endpoint"""

    @extend_schema(
        summary="Refresh token",
        description="Refresh access token using refresh token",
        request=TokenRefreshSerializer,
        responses={200: "Token refreshed", 400: "Invalid refresh token"},
    )
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh"]
            try:
                refresh = RefreshToken(refresh_token)
                return Response(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    }
                )
            except Exception:
                return Response(
                    {"error": "Invalid refresh token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Logout endpoint"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="User logout",
        description="Logout user and blacklist refresh token",
        request=LogoutSerializer,
        responses={200: "Logout successful"},
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data["refresh"]
                refresh = RefreshToken(refresh_token)
                refresh.blacklist()

                # Log activity
                UserActivity.objects.create(
                    user=request.user,
                    activity_type="logout",
                    description="User logged out",
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                )

                return Response({"message": "Logout successful"})
            except Exception:
                # Even if token blacklisting fails, return success
                return Response({"message": "Logout successful"})
        return Response({"message": "Logout successful"})


class PasswordChangeView(APIView):
    """Password change endpoint"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Change password",
        description="Change user password",
        request=PasswordChangeSerializer,
        responses={200: "Password changed", 400: "Invalid password"},
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]

            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()

                # Log activity
                UserActivity.objects.create(
                    user=user,
                    activity_type="password_changed",
                    description="User changed password",
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                )

                return Response({"message": "Password changed successfully"})
            else:
                return Response(
                    {"error": "Invalid old password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class UserStatsView(APIView):
    """User statistics endpoint"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get user statistics",
        description="Get user statistics and activity summary",
        responses={200: UserStatsSerializer},
    )
    def get(self, request):
        user = request.user

        # Calculate statistics
        total_documents = Document.objects.filter(owner=user).count()
        shared_documents = DocumentShare.objects.filter(shared_by=user).count()
        received_documents = DocumentShare.objects.filter(shared_with=user).count()
        pending_requests = DocumentRequest.objects.filter(
            requestee=user, status="pending"
        ).count()

        # Try to get QR shares count (sharing app might not be available)
        try:
            from sharing.models import QRCodeShare

            qr_shares_created = QRCodeShare.objects.filter(created_by=user).count()
        except ImportError:
            qr_shares_created = 0

        # Get last activity
        last_activity = (
            UserActivity.objects.filter(user=user).order_by("-created_at").first()
        )
        last_activity_time = (
            last_activity.created_at if last_activity else user.last_login
        )

        stats = {
            "total_documents": total_documents,
            "shared_documents": shared_documents,
            "received_documents": received_documents,
            "pending_requests": pending_requests,
            "qr_shares_created": qr_shares_created,
            "last_activity": last_activity_time,
        }

        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


class NotificationPreferencesView(APIView):
    """Notification preferences management"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get notification preferences",
        description="Get user notification preferences",
        responses={200: NotificationPreferencesSerializer},
    )
    def get(self, request):
        preferences = request.user.notification_preferences
        serializer = NotificationPreferencesSerializer(preferences)
        return Response(serializer.data)

    @extend_schema(
        summary="Update notification preferences",
        description="Update user notification preferences",
        request=NotificationPreferencesSerializer,
        responses={200: NotificationPreferencesSerializer},
    )
    def put(self, request):
        serializer = NotificationPreferencesSerializer(data=request.data)
        if serializer.is_valid():
            request.user.notification_preferences = serializer.validated_data
            request.user.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrivacySettingsView(APIView):
    """Privacy settings management"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get privacy settings",
        description="Get user privacy settings",
        responses={200: PrivacySettingsSerializer},
    )
    def get(self, request):
        settings = request.user.privacy_settings
        serializer = PrivacySettingsSerializer(settings)
        return Response(serializer.data)

    @extend_schema(
        summary="Update privacy settings",
        description="Update user privacy settings",
        request=PrivacySettingsSerializer,
        responses={200: PrivacySettingsSerializer},
    )
    def put(self, request):
        serializer = PrivacySettingsSerializer(data=request.data)
        if serializer.is_valid():
            request.user.privacy_settings = serializer.validated_data
            request.user.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserActivityListView(generics.ListAPIView):
    """User activity list"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserActivitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activity_type", "created_at"]

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    @extend_schema(
        summary="Get user activities",
        description="Get list of user activities",
        parameters=[
            OpenApiParameter(
                name="activity_type",
                description="Filter by activity type",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="created_at",
                description="Filter by creation date",
                required=False,
                type=str,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserSecuritySettingsView(APIView):
    """User security settings management"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get security settings",
        description="Retrieve user's security settings including PIN and biometric preferences",
        responses={200: UserSecuritySettingsSerializer},
    )
    def get(self, request):
        security_settings, created = UserSecuritySettings.objects.get_or_create(
            user=request.user
        )
        serializer = UserSecuritySettingsSerializer(security_settings)
        return Response(serializer.data)

    @extend_schema(
        summary="Update security settings",
        description="Update user's security settings including PIN and biometric preferences",
        request=SecuritySettingsUpdateSerializer,
        responses={200: UserSecuritySettingsSerializer, 400: "Bad Request"},
    )
    def put(self, request):
        security_settings, created = UserSecuritySettings.objects.get_or_create(
            user=request.user
        )
        serializer = SecuritySettingsUpdateSerializer(
            security_settings, data=request.data, partial=True
        )

        if serializer.is_valid():
            # Handle PIN update if provided
            if (
                "new_pin" in serializer.validated_data
                and serializer.validated_data["new_pin"]
            ):
                # In a real implementation, you would hash the PIN here
                # For now, we'll store it as-is (NOT recommended for production)
                security_settings.secret_pin = serializer.validated_data["new_pin"]
                security_settings.pin_created_at = timezone.now()
                serializer.validated_data.pop("new_pin", None)
                serializer.validated_data.pop("current_pin", None)

            serializer.save()

            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type="security_settings_updated",
                description="User updated security settings",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            return Response(UserSecuritySettingsSerializer(security_settings).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class PINVerificationView(APIView):
    """PIN verification endpoint"""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Verify PIN",
        description="Verify user's secret PIN for sensitive operations",
        request=PINVerificationSerializer,
        responses={200: "PIN verified", 400: "Invalid PIN"},
    )
    def post(self, request):
        serializer = PINVerificationSerializer(data=request.data)
        if serializer.is_valid():
            pin = serializer.validated_data["pin"]

            try:
                security_settings = request.user.security_settings
                if not security_settings.secret_pin:
                    return Response(
                        {"error": "No PIN is set"}, status=status.HTTP_400_BAD_REQUEST
                    )

                # In a real implementation, you would verify the hashed PIN here
                # For now, we'll do a simple comparison (NOT recommended for production)
                if security_settings.secret_pin == pin:
                    # Update last used timestamp
                    security_settings.pin_last_used = timezone.now()
                    security_settings.save()

                    # Log activity
                    UserActivity.objects.create(
                        user=request.user,
                        activity_type="pin_verified",
                        description="User verified PIN successfully",
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    )

                    return Response({"message": "PIN verified successfully"})
                else:
                    return Response(
                        {"error": "Invalid PIN"}, status=status.HTTP_400_BAD_REQUEST
                    )

            except UserSecuritySettings.DoesNotExist:
                return Response(
                    {"error": "Security settings not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
