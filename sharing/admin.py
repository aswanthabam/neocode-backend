from django.contrib import admin
from .models import (
    QRCodeShare, ShareSession, SharingActivity, DocumentRequestResponse,
    ShareNotification
)


@admin.register(QRCodeShare)
class QRCodeShareAdmin(admin.ModelAdmin):
    list_display = ('document', 'created_by', 'title', 'permission', 'status', 'current_views', 'max_views', 'expires_at', 'created_at')
    list_filter = ('permission', 'status', 'created_at')
    search_fields = ('document__title', 'created_by__email', 'title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'current_views', 'qr_code_image', 'is_expired', 'is_view_limit_reached', 'is_active', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {'fields': ('id', 'document', 'created_by', 'title', 'description')}),
        ('Access Control', {'fields': ('permission', 'expires_at', 'max_views', 'current_views')}),
        ('QR Code', {'fields': ('qr_code_image',)}),
        ('Status', {'fields': ('status', 'is_expired', 'is_view_limit_reached', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    def is_view_limit_reached(self, obj):
        return obj.is_view_limit_reached
    is_view_limit_reached.boolean = True
    is_view_limit_reached.short_description = 'View Limit Reached'
    
    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Active'


@admin.register(ShareSession)
class ShareSessionAdmin(admin.ModelAdmin):
    list_display = ('qr_share', 'session_token_short', 'ip_address', 'status', 'accessed_at', 'expires_at')
    list_filter = ('status', 'accessed_at')
    search_fields = ('qr_share__document__title', 'session_token', 'ip_address')
    ordering = ('-accessed_at',)
    readonly_fields = ('id', 'session_token', 'is_expired', 'accessed_at')
    
    fieldsets = (
        ('Session Info', {'fields': ('id', 'qr_share', 'session_token')}),
        ('Access Details', {'fields': ('ip_address', 'user_agent')}),
        ('Status', {'fields': ('status', 'is_expired', 'expires_at')}),
        ('Timestamps', {'fields': ('accessed_at',)}),
    )
    
    def session_token_short(self, obj):
        return obj.session_token[:8] + '...' if len(obj.session_token) > 8 else obj.session_token
    session_token_short.short_description = 'Session Token'
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(SharingActivity)
class SharingActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'document', 'description', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__email', 'user__full_name', 'document__title', 'description')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Activity Info', {'fields': ('user', 'activity_type', 'description')}),
        ('Related Objects', {'fields': ('document', 'qr_share', 'share_session', 'document_request')}),
        ('Access Details', {'fields': ('ip_address', 'user_agent')}),
        ('Metadata', {'fields': ('metadata',)}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False  # Activities should only be created by the system


@admin.register(DocumentRequestResponse)
class DocumentRequestResponseAdmin(admin.ModelAdmin):
    list_display = ('request', 'responder', 'response', 'shared_document', 'responded_at')
    list_filter = ('response', 'responded_at')
    search_fields = ('request__title', 'responder__email', 'responder__full_name', 'message')
    ordering = ('-responded_at',)
    
    fieldsets = (
        ('Response Info', {'fields': ('request', 'responder', 'response')}),
        ('Details', {'fields': ('message', 'shared_document')}),
        ('Timestamps', {'fields': ('responded_at',)}),
    )
    
    readonly_fields = ('responded_at',)


@admin.register(ShareNotification)
class ShareNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'user__full_name', 'title', 'message')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Notification Info', {'fields': ('user', 'notification_type', 'title', 'message')}),
        ('Related Objects', {'fields': ('document', 'qr_share', 'document_request')}),
        ('Status', {'fields': ('is_read', 'read_at')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    readonly_fields = ('created_at',)
    
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"
