from django.db import models
from django.conf import settings
from django.utils import timezone
from common.fields import DocumentFileField
import uuid
import os


class DocumentCategory(models.Model):
    """Document categories for organization"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Document Category'
        verbose_name_plural = 'Document Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Document(models.Model):
    """Document model with encryption and metadata"""
    # Basic information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # File information - Using Supabase storage
    file = DocumentFileField(upload_to='documents/')
    file_size = models.BigIntegerField(blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    original_filename = models.CharField(max_length=255)
    
    # Ownership and access
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_documents')
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Trust levels
    TRUST_LEVEL_CHOICES = [
        ('user_uploaded', 'User Uploaded'),
        ('peer_shared', 'Peer Shared'),
        ('officially_issued', 'Officially Issued'),
    ]
    trust_level = models.CharField(max_length=20, choices=TRUST_LEVEL_CHOICES, default='user_uploaded')
    
    # Issuer information (for officially issued documents)
    issuer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='issued_documents'
    )
    issue_date = models.DateTimeField(blank=True, null=True)
    
    # Document status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Encryption and security
    is_encrypted = models.BooleanField(default=True)
    encryption_key_hash = models.CharField(max_length=255, blank=True, null=True)
    
    # Expiry and versioning
    expiry_date = models.DateTimeField(blank=True, null=True)
    version = models.PositiveIntegerField(default=1)
    parent_document = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='versions')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.owner.email}"
    
    def save(self, *args, **kwargs):
        # Set file information if not already set
        if self.file and not self.file_size:
            self.file_size = self.file.size
        if self.file and not self.file_type:
            self.file_type = os.path.splitext(self.file.name)[1]
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if document is expired"""
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False
    
    @property
    def download_count(self):
        """Get total download count"""
        return self.access_logs.filter(action='download').count()
    
    @property
    def view_count(self):
        """Get total view count"""
        return self.access_logs.filter(action='view').count()
    
    def get_file_url(self):
        """Get the public URL for the document file"""
        if self.file:
            from common.storage import get_file_url
            return get_file_url(self.file.name, 'documents')
        return None


class DocumentAccess(models.Model):
    """Track document access permissions"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='access_permissions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('download', 'Download'),
        ('edit', 'Edit'),
        ('admin', 'Admin'),
    ]
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='view')
    
    # Access control
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='granted_access'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Document Access'
        verbose_name_plural = 'Document Access'
        unique_together = ['document', 'user']
    
    def __str__(self):
        return f"{self.user.email} - {self.document.title} ({self.permission})"


class DocumentAccessLog(models.Model):
    """Log document access for audit trail"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    ACTION_CHOICES = [
        ('view', 'View'),
        ('download', 'Download'),
        ('edit', 'Edit'),
        ('share', 'Share'),
        ('revoke', 'Revoke'),
    ]
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Access details
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Document Access Log'
        verbose_name_plural = 'Document Access Logs'
        ordering = ['-accessed_at']
    
    def __str__(self):
        return f"{self.user.email} {self.action} {self.document.title}"


class DocumentShare(models.Model):
    """Document sharing between users"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_documents')
    shared_with = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_documents')
    
    # Share settings
    permission = models.CharField(max_length=20, choices=DocumentAccess.PERMISSION_CHOICES, default='view')
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Share status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Document Share'
        verbose_name_plural = 'Document Shares'
        unique_together = ['document', 'shared_with']
    
    def __str__(self):
        return f"{self.document.title} shared by {self.shared_by.email} with {self.shared_with.email}"


class DocumentRequest(models.Model):
    """Document requests between users"""
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_requests_sent')
    requestee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='document_requests_received')
    
    # Request details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Request status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Response
    response_message = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Document Request'
        verbose_name_plural = 'Document Requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.requester.email} requests {self.title} from {self.requestee.email}"
