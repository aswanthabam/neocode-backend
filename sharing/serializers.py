from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    QRCodeShare, ShareSession, SharingActivity, DocumentRequestResponse,
    ShareNotification
)
from documents.models import Document, DocumentRequest

User = get_user_model()


class QRCodeShareSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    qr_code_url = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    is_view_limit_reached = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = QRCodeShare
        fields = [
            'id', 'document', 'document_title', 'created_by', 'created_by_email',
            'created_by_name', 'title', 'description', 'permission', 'expires_at',
            'max_views', 'current_views', 'qr_code_image', 'qr_code_url',
            'status', 'is_expired', 'is_view_limit_reached', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_by', 'current_views', 'qr_code_image', 'qr_code_url',
            'is_expired', 'is_view_limit_reached', 'is_active', 'created_at', 'updated_at'
        ]
    
    def get_qr_code_url(self, obj):
        if obj.qr_code_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.qr_code_image.url)
        return None


class QRCodeShareCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCodeShare
        fields = ['document', 'title', 'description', 'permission', 'expires_at', 'max_views']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ShareSessionSerializer(serializers.ModelSerializer):
    qr_share_title = serializers.CharField(source='qr_share.title', read_only=True)
    document_title = serializers.CharField(source='qr_share.document.title', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ShareSession
        fields = [
            'id', 'qr_share', 'qr_share_title', 'document_title', 'session_token',
            'ip_address', 'user_agent', 'accessed_at', 'expires_at', 'status', 'is_expired'
        ]
        read_only_fields = [
            'id', 'session_token', 'ip_address', 'user_agent', 'accessed_at', 'is_expired'
        ]


class ShareSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareSession
        fields = ['qr_share']
    
    def create(self, validated_data):
        # Generate session token
        import secrets
        session_token = secrets.token_urlsafe(32)
        
        # Set expiry (1 hour from now)
        from django.utils import timezone
        from datetime import timedelta
        expires_at = timezone.now() + timedelta(hours=1)
        
        validated_data['session_token'] = session_token
        validated_data['expires_at'] = expires_at
        
        # Get client IP and user agent
        request = self.context['request']
        validated_data['ip_address'] = self.get_client_ip(request)
        validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return super().create(validated_data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SharingActivitySerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = SharingActivity
        fields = [
            'id', 'user', 'user_email', 'user_name', 'activity_type',
            'document', 'document_title', 'qr_share', 'share_session',
            'document_request', 'description', 'metadata', 'ip_address',
            'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'ip_address', 'user_agent', 'created_at']


class DocumentRequestResponseSerializer(serializers.ModelSerializer):
    requester_email = serializers.EmailField(source='request.requester.email', read_only=True)
    requester_name = serializers.CharField(source='request.requester.full_name', read_only=True)
    requestee_email = serializers.EmailField(source='request.requestee.email', read_only=True)
    requestee_name = serializers.CharField(source='request.requestee.full_name', read_only=True)
    request_title = serializers.CharField(source='request.title', read_only=True)
    responder_email = serializers.EmailField(source='responder.email', read_only=True)
    responder_name = serializers.CharField(source='responder.full_name', read_only=True)
    shared_document_title = serializers.CharField(source='shared_document.title', read_only=True)
    
    class Meta:
        model = DocumentRequestResponse
        fields = [
            'id', 'request', 'requester_email', 'requester_name',
            'requestee_email', 'requestee_name', 'request_title',
            'responder', 'responder_email', 'responder_name', 'response',
            'message', 'shared_document', 'shared_document_title', 'responded_at'
        ]
        read_only_fields = ['id', 'responder', 'responded_at']


class DocumentRequestResponseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequestResponse
        fields = ['request', 'response', 'message', 'shared_document']
    
    def create(self, validated_data):
        validated_data['responder'] = self.context['request'].user
        
        # Update the original request status
        request = validated_data['request']
        if validated_data['response'] == 'approve':
            request.status = 'approved'
        elif validated_data['response'] == 'decline':
            request.status = 'declined'
        else:
            request.status = 'pending'
        request.save()
        
        return super().create(validated_data)


class ShareNotificationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = ShareNotification
        fields = [
            'id', 'user', 'user_email', 'user_name', 'notification_type',
            'document', 'document_title', 'qr_share', 'document_request',
            'title', 'message', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'is_read', 'read_at', 'created_at']


class ShareNotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareNotification
        fields = ['is_read']


class QRCodeAccessSerializer(serializers.Serializer):
    """Serializer for accessing documents via QR code"""
    qr_share_id = serializers.UUIDField()
    session_token = serializers.CharField(required=False)
    
    def validate_qr_share_id(self, value):
        try:
            qr_share = QRCodeShare.objects.get(id=value)
            if not qr_share.is_active:
                raise serializers.ValidationError("QR code is no longer active")
        except QRCodeShare.DoesNotExist:
            raise serializers.ValidationError("Invalid QR code")
        return value


class DocumentAccessViaQRSerializer(serializers.Serializer):
    """Serializer for document access via QR code"""
    document_title = serializers.CharField()
    document_description = serializers.CharField()
    permission = serializers.CharField()
    expires_at = serializers.DateTimeField()
    created_by_name = serializers.CharField()
    access_url = serializers.CharField()
    download_url = serializers.CharField(required=False)


class ShareStatsSerializer(serializers.Serializer):
    """Serializer for sharing statistics"""
    total_qr_shares = serializers.IntegerField()
    active_qr_shares = serializers.IntegerField()
    total_sessions = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    total_requests_sent = serializers.IntegerField()
    total_requests_received = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    total_notifications = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()


class BulkShareSerializer(serializers.Serializer):
    """Serializer for bulk sharing operations"""
    document_ids = serializers.ListField(child=serializers.UUIDField())
    target_users = serializers.ListField(child=serializers.IntegerField(), required=False)
    permission = serializers.CharField(default='view')
    expires_at = serializers.DateTimeField(required=False)
    message = serializers.CharField(required=False)


class QRCodeBulkCreateSerializer(serializers.Serializer):
    """Serializer for creating multiple QR codes"""
    document_ids = serializers.ListField(child=serializers.UUIDField())
    title = serializers.CharField()
    description = serializers.CharField(required=False)
    permission = serializers.CharField(default='view')
    expires_at = serializers.DateTimeField()
    max_views = serializers.IntegerField(default=1)


class ShareActivityFilterSerializer(serializers.Serializer):
    """Serializer for filtering sharing activities"""
    activity_type = serializers.CharField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    user = serializers.IntegerField(required=False)
    document = serializers.UUIDField(required=False) 