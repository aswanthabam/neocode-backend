from django.contrib import admin
from .models import (
    DocumentCategory, Document, DocumentAccess, DocumentAccessLog,
    DocumentShare, DocumentRequest
)


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'description', 'icon')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    readonly_fields = ('created_at',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'trust_level', 'status', 'file_size', 'created_at')
    list_filter = ('trust_level', 'status', 'category', 'is_encrypted', 'created_at')
    search_fields = ('title', 'description', 'owner__email', 'owner__full_name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'file_size', 'file_type', 'download_count', 'view_count', 'is_expired', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {'fields': ('id', 'title', 'description', 'owner')}),
        ('File Info', {'fields': ('file', 'file_size', 'file_type', 'original_filename')}),
        ('Classification', {'fields': ('category', 'trust_level', 'issuer', 'issue_date')}),
        ('Status', {'fields': ('status', 'is_encrypted', 'encryption_key_hash')}),
        ('Metadata', {'fields': ('tags', 'metadata', 'expiry_date', 'version', 'parent_document')}),
        ('Statistics', {'fields': ('download_count', 'view_count', 'is_expired')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def download_count(self, obj):
        return obj.download_count
    download_count.short_description = 'Downloads'
    
    def view_count(self, obj):
        return obj.view_count
    view_count.short_description = 'Views'
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


@admin.register(DocumentAccess)
class DocumentAccessAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'permission', 'granted_by', 'granted_at', 'expires_at')
    list_filter = ('permission', 'granted_at')
    search_fields = ('document__title', 'user__email', 'user__full_name', 'granted_by__email')
    ordering = ('-granted_at',)
    
    fieldsets = (
        ('Access Info', {'fields': ('document', 'user', 'permission')}),
        ('Grant Details', {'fields': ('granted_by', 'granted_at', 'expires_at')}),
        ('Notes', {'fields': ('notes',)}),
    )
    
    readonly_fields = ('granted_at',)


@admin.register(DocumentAccessLog)
class DocumentAccessLogAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'action', 'ip_address', 'accessed_at')
    list_filter = ('action', 'accessed_at')
    search_fields = ('document__title', 'user__email', 'user__full_name', 'ip_address')
    ordering = ('-accessed_at',)
    
    fieldsets = (
        ('Access Info', {'fields': ('document', 'user', 'action')}),
        ('Access Details', {'fields': ('ip_address', 'user_agent', 'session_id')}),
        ('Timestamps', {'fields': ('accessed_at',)}),
    )
    
    readonly_fields = ('accessed_at',)
    
    def has_add_permission(self, request):
        return False  # Logs should only be created by the system


@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = ('document', 'shared_by', 'shared_with', 'permission', 'status', 'created_at')
    list_filter = ('permission', 'status', 'created_at')
    search_fields = ('document__title', 'shared_by__email', 'shared_with__email')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Share Info', {'fields': ('document', 'shared_by', 'shared_with', 'permission')}),
        ('Settings', {'fields': ('expires_at', 'status')}),
        ('Message', {'fields': ('message',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'requester', 'requestee', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'requester__email', 'requestee__email')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Request Info', {'fields': ('requester', 'requestee', 'title', 'description', 'category')}),
        ('Status', {'fields': ('status', 'response_message', 'responded_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
