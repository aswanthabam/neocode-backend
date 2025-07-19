from django.db import models
from django.conf import settings
from django.utils import timezone
from common.fields import QRCodeImageField
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image


class QRCodeShare(models.Model):
    """QR code for temporary document sharing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey('documents.Document', on_delete=models.CASCADE, related_name='qr_shares')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_qr_shares')
    
    # QR code settings
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Access control
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('download', 'Download'),
    ]
    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='view')
    
    # Expiry settings
    expires_at = models.DateTimeField()
    max_views = models.PositiveIntegerField(default=1)
    current_views = models.PositiveIntegerField(default=0)
    
    # QR code image - Using Supabase storage
    qr_code_image = QRCodeImageField(upload_to='qr-codes/', blank=True, null=True)
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'QR Code Share'
        verbose_name_plural = 'QR Code Shares'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"QR Share: {self.document.title} by {self.created_by.email}"
    
    def save(self, *args, **kwargs):
        if not self.qr_code_image:
            self.generate_qr_code()
        super().save(*args, **kwargs)
    
    def generate_qr_code(self):
        """Generate QR code for this share"""
        # Create the share URL
        share_url = f"https://yourdomain.com/sharing/access/{self.id}/"
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(share_url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to Django file
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f"qr_share_{self.id}.png"
        
        self.qr_code_image.save(filename, ContentFile(buffer.getvalue()), save=False)
    
    def get_qr_code_url(self):
        """Get the public URL for the QR code image"""
        if self.qr_code_image:
            from common.storage import get_file_url
            return get_file_url(self.qr_code_image.name, 'qr-codes')
        return None
    
    @property
    def is_expired(self):
        """Check if QR share is expired"""
        return timezone.now() > self.expires_at
    
    @property
    def is_view_limit_reached(self):
        """Check if view limit is reached"""
        return self.current_views >= self.max_views
    
    @property
    def is_active(self):
        """Check if QR share is still active"""
        return (self.status == 'active' and 
                not self.is_expired and 
                not self.is_view_limit_reached)


class ShareSession(models.Model):
    """Temporary session for accessing shared documents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_share = models.ForeignKey(QRCodeShare, on_delete=models.CASCADE, related_name='sessions')
    
    # Session details
    session_token = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Access tracking
    accessed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    class Meta:
        verbose_name = 'Share Session'
        verbose_name_plural = 'Share Sessions'
        ordering = ['-accessed_at']
    
    def __str__(self):
        return f"Session: {self.session_token[:8]}... for {self.qr_share.document.title}"
    
    @property
    def is_expired(self):
        """Check if session is expired"""
        return timezone.now() > self.expires_at


class SharingActivity(models.Model):
    """Track all sharing activities for audit trail"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sharing_activities')
    
    # Activity details
    ACTIVITY_TYPE_CHOICES = [
        ('qr_created', 'QR Code Created'),
        ('qr_accessed', 'QR Code Accessed'),
        ('document_shared', 'Document Shared'),
        ('document_requested', 'Document Requested'),
        ('request_responded', 'Request Responded'),
        ('access_granted', 'Access Granted'),
        ('access_revoked', 'Access Revoked'),
    ]
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    
    # Related objects
    document = models.ForeignKey('documents.Document', on_delete=models.CASCADE, null=True, blank=True)
    qr_share = models.ForeignKey(QRCodeShare, on_delete=models.CASCADE, null=True, blank=True)
    share_session = models.ForeignKey(ShareSession, on_delete=models.CASCADE, null=True, blank=True)
    document_request = models.ForeignKey('documents.DocumentRequest', on_delete=models.CASCADE, null=True, blank=True)
    
    # Activity details
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    # Access details
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Sharing Activity'
        verbose_name_plural = 'Sharing Activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()} - {self.created_at}"


class DocumentRequestResponse(models.Model):
    """Track responses to document requests"""
    request = models.ForeignKey('documents.DocumentRequest', on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='request_responses')
    
    # Response details
    RESPONSE_CHOICES = [
        ('approve', 'Approve'),
        ('decline', 'Decline'),
        ('request_info', 'Request More Information'),
    ]
    response = models.CharField(max_length=20, choices=RESPONSE_CHOICES)
    
    # Response message
    message = models.TextField(blank=True, null=True)
    
    # Shared document (if approved)
    shared_document = models.ForeignKey('documents.Document', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    responded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Document Request Response'
        verbose_name_plural = 'Document Request Responses'
        ordering = ['-responded_at']
    
    def __str__(self):
        return f"{self.responder.email} {self.response} request from {self.request.requester.email}"


class ShareNotification(models.Model):
    """Notifications for sharing activities"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='share_notifications')
    
    # Notification details
    NOTIFICATION_TYPE_CHOICES = [
        ('document_shared', 'Document Shared'),
        ('document_requested', 'Document Requested'),
        ('request_responded', 'Request Responded'),
        ('access_granted', 'Access Granted'),
        ('qr_accessed', 'QR Code Accessed'),
    ]
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    
    # Related objects
    document = models.ForeignKey('documents.Document', on_delete=models.CASCADE, null=True, blank=True)
    qr_share = models.ForeignKey(QRCodeShare, on_delete=models.CASCADE, null=True, blank=True)
    document_request = models.ForeignKey('documents.DocumentRequest', on_delete=models.CASCADE, null=True, blank=True)
    
    # Notification content
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Share Notification'
        verbose_name_plural = 'Share Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
