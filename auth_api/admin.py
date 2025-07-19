from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OAuthToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'username', 'is_oauth_user', 'is_active', 'created_at', 'last_login')
    list_filter = ('is_oauth_user', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'full_name', 'username')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'username', 'profile_picture')}),
        ('OAuth info', {'fields': ('google_id', 'is_oauth_user')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'username', 'password1', 'password2'),
        }),
    )


@admin.register(OAuthToken)
class OAuthTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_type', 'expires_at', 'created_at')
    list_filter = ('token_type', 'created_at')
    search_fields = ('user__email', 'user__full_name')
    readonly_fields = ('created_at',)
