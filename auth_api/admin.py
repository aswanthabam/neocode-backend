from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Organization, OAuthToken, UserActivity


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'username', 'vault_id', 'user_type', 'is_verified', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_oauth_user', 'created_at')
    search_fields = ('email', 'full_name', 'username', 'vault_id')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'username', 'vault_id', 'user_type', 'phone_number', 'date_of_birth', 'address', 'profile_picture')}),
        ('Organization info', {'fields': ('organization_name', 'organization_type', 'organization_website', 'organization_address', 'organization_phone')}),
        ('Verification', {'fields': ('is_verified', 'verification_date', 'verified_by')}),
        ('OAuth', {'fields': ('google_id', 'is_oauth_user')}),
        ('Preferences', {'fields': ('notification_preferences', 'privacy_settings')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'username', 'password1', 'password2', 'user_type'),
        }),
    )
    
    readonly_fields = ('vault_id', 'created_at', 'updated_at')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'organization_type', 'is_verified', 'can_issue_documents', 'can_request_documents', 'created_at')
    list_filter = ('organization_type', 'is_verified', 'can_issue_documents', 'can_request_documents', 'created_at')
    search_fields = ('name', 'user__email', 'user__full_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Info', {'fields': ('user', 'name', 'description', 'organization_type')}),
        ('Contact Info', {'fields': ('website', 'email', 'phone', 'address')}),
        ('Capabilities', {'fields': ('can_issue_documents', 'can_request_documents')}),
        ('Verification', {'fields': ('is_verified', 'verification_date', 'verified_by')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(OAuthToken)
class OAuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_type', 'expires_at', 'created_at')
    list_filter = ('token_type', 'created_at')
    search_fields = ('user__email', 'user__full_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Token Info', {'fields': ('user', 'access_token', 'refresh_token', 'token_type')}),
        ('Expiry', {'fields': ('expires_at',)}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    readonly_fields = ('created_at',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'description', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email', 'user__full_name', 'description')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Activity Info', {'fields': ('user', 'activity_type', 'description')}),
        ('Access Details', {'fields': ('ip_address', 'user_agent')}),
        ('Metadata', {'fields': ('metadata',)}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False  # Activities should only be created by the system
