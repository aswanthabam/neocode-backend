from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from common.fields import ProfileImageField
import uuid


class CustomUser(AbstractUser):
    # Basic user fields
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)

    # Vault ID system
    vault_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="Unique vault identifier (username@vault)",
    )

    # User type and roles
    USER_TYPE_CHOICES = [
        ("individual", "Individual"),
        ("organization", "Organization"),
    ]
    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default="individual"
    )

    # Organization fields
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    organization_type = models.CharField(max_length=100, blank=True, null=True)
    organization_website = models.URLField(blank=True, null=True)
    organization_address = models.TextField(blank=True, null=True)
    organization_phone = models.CharField(max_length=20, blank=True, null=True)

    # Verification fields
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )

    # OAuth fields
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    profile_picture = ProfileImageField(
        upload_to="profile-images/", blank=True, null=True
    )
    is_oauth_user = models.BooleanField(default=False)

    # Contact information
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
    )
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Preferences
    notification_preferences = models.JSONField(default=dict, blank=True)
    privacy_settings = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "username"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Generate vault_id if not provided
        if not self.vault_id:
            username = self.username or self.email.split("@")[0]
            self.vault_id = f"{username}@vault"
        super().save(*args, **kwargs)

    def get_profile_picture_url(self):
        """Get the public URL for the profile picture"""
        if self.profile_picture:
            from common.storage import get_file_url

            return get_file_url(self.profile_picture.name, "profile-images")
        return None

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Organization(models.Model):
    """Organization model for document issuers and requesters"""

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="organization_profile"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    ORGANIZATION_TYPE_CHOICES = [
        ("government", "Government"),
        ("educational", "Educational"),
        ("financial", "Financial"),
        ("healthcare", "Healthcare"),
        ("corporate", "Corporate"),
        ("non_profit", "Non-Profit"),
        ("other", "Other"),
    ]
    organization_type = models.CharField(
        max_length=20, choices=ORGANIZATION_TYPE_CHOICES
    )

    # Contact information
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Verification and status
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="verified_organizations",
    )

    # Document issuance capabilities
    can_issue_documents = models.BooleanField(default=False)
    can_request_documents = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"


class OAuthToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_type = models.CharField(max_length=50, default="Bearer")
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.email}"

    class Meta:
        verbose_name = "OAuth Token"
        verbose_name_plural = "OAuth Tokens"


class UserActivity(models.Model):
    """Track user activities for audit trail"""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Activity"
        verbose_name_plural = "User Activities"
        ordering = ["-created_at"]


class UserSecuritySettings(models.Model):
    """User security settings for PIN and biometric authentication"""

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="security_settings"
    )

    # Secret PIN (hashed)
    secret_pin = models.CharField(
        max_length=255, blank=True, null=True, help_text="Hashed secret PIN"
    )
    pin_created_at = models.DateTimeField(blank=True, null=True)
    pin_last_used = models.DateTimeField(blank=True, null=True)

    # Biometric settings
    biometric_enabled = models.BooleanField(
        default=False, help_text="Whether biometric authentication is enabled"
    )
    biometric_type = models.CharField(
        max_length=20,
        choices=[
            ("fingerprint", "Fingerprint"),
            ("face", "Face Recognition"),
            ("touch", "Touch ID"),
            ("face_id", "Face ID"),
        ],
        blank=True,
        null=True,
    )

    # Security preferences
    require_pin_for_downloads = models.BooleanField(
        default=True, help_text="Require PIN for document downloads"
    )
    require_pin_for_sharing = models.BooleanField(
        default=True, help_text="Require PIN for document sharing"
    )
    require_pin_for_deletion = models.BooleanField(
        default=True, help_text="Require PIN for document deletion"
    )

    # Session security
    auto_lock_timeout = models.IntegerField(
        default=300, help_text="Auto-lock timeout in seconds (0 = disabled)"
    )
    max_login_attempts = models.IntegerField(
        default=5, help_text="Maximum failed login attempts"
    )
    lockout_duration = models.IntegerField(
        default=900, help_text="Lockout duration in seconds"
    )

    # Two-factor authentication
    two_factor_enabled = models.BooleanField(
        default=False, help_text="Whether 2FA is enabled"
    )
    backup_codes = models.JSONField(
        default=list, blank=True, help_text="Backup codes for 2FA"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Security settings for {self.user.email}"

    class Meta:
        verbose_name = "User Security Settings"
        verbose_name_plural = "User Security Settings"
