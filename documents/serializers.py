from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    DocumentCategory, Document, DocumentAccess, DocumentAccessLog,
    DocumentShare, DocumentRequest
)
from django.utils import timezone

User = get_user_model()


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ['id', 'name', 'description', 'icon', 'is_active', 'created_at']


class DocumentCategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ['name', 'description', 'icon']


class DocumentSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    issuer_name = serializers.CharField(source='issuer.full_name', read_only=True)
    download_count = serializers.IntegerField(read_only=True)
    view_count = serializers.IntegerField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'file', 'file_size', 'file_type',
            'original_filename', 'owner', 'owner_email', 'owner_name',
            'category', 'category_name', 'trust_level', 'issuer', 'issuer_name',
            'issue_date', 'status', 'tags', 'metadata', 'is_encrypted',
            'expiry_date', 'version', 'download_count', 'view_count',
            'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'owner', 'owner_email', 'owner_name', 'file_size',
            'file_type', 'download_count', 'view_count', 'is_expired',
            'created_at', 'updated_at'
        ]


class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'title', 'description', 'file', 'category', 'trust_level',
            'tags', 'metadata', 'expiry_date'
        ]
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        validated_data['original_filename'] = validated_data['file'].name
        return super().create(validated_data)


class DocumentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'title', 'description', 'category', 'tags', 'metadata',
            'expiry_date', 'status'
        ]


class DocumentAccessSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.full_name', read_only=True)
    
    class Meta:
        model = DocumentAccess
        fields = [
            'id', 'document', 'document_title', 'user', 'user_email',
            'user_name', 'permission', 'granted_by', 'granted_by_name',
            'granted_at', 'expires_at', 'notes'
        ]
        read_only_fields = ['id', 'granted_by', 'granted_at']


class DocumentAccessCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentAccess
        fields = ['document', 'user', 'permission', 'expires_at', 'notes']
    
    def create(self, validated_data):
        validated_data['granted_by'] = self.context['request'].user
        return super().create(validated_data)


class DocumentAccessLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = DocumentAccessLog
        fields = [
            'id', 'document', 'document_title', 'user', 'user_email',
            'user_name', 'action', 'ip_address', 'user_agent', 'session_id',
            'accessed_at'
        ]
        read_only_fields = ['id', 'ip_address', 'user_agent', 'session_id', 'accessed_at']


class DocumentShareSerializer(serializers.ModelSerializer):
    shared_by_email = serializers.EmailField(source='shared_by.email', read_only=True)
    shared_by_name = serializers.CharField(source='shared_by.full_name', read_only=True)
    shared_with_email = serializers.EmailField(source='shared_with.email', read_only=True)
    shared_with_name = serializers.CharField(source='shared_with.full_name', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = DocumentShare
        fields = [
            'id', 'document', 'document_title', 'shared_by', 'shared_by_email',
            'shared_by_name', 'shared_with', 'shared_with_email', 'shared_with_name',
            'permission', 'expires_at', 'status', 'message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shared_by', 'status', 'created_at', 'updated_at']


class DocumentShareCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentShare
        fields = ['document', 'shared_with', 'permission', 'expires_at', 'message']
    
    def create(self, validated_data):
        validated_data['shared_by'] = self.context['request'].user
        return super().create(validated_data)


class DocumentRequestSerializer(serializers.ModelSerializer):
    requester_email = serializers.EmailField(source='requester.email', read_only=True)
    requester_name = serializers.CharField(source='requester.full_name', read_only=True)
    requestee_email = serializers.EmailField(source='requestee.email', read_only=True)
    requestee_name = serializers.CharField(source='requestee.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = DocumentRequest
        fields = [
            'id', 'requester', 'requester_email', 'requester_name',
            'requestee', 'requestee_email', 'requestee_name', 'title',
            'description', 'category', 'category_name', 'status',
            'response_message', 'responded_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'requester', 'status', 'response_message', 'responded_at', 'created_at', 'updated_at']


class DocumentRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequest
        fields = ['requestee', 'title', 'description', 'category']
    
    def create(self, validated_data):
        validated_data['requester'] = self.context['request'].user
        return super().create(validated_data)


class DocumentRequestResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRequest
        fields = ['status', 'response_message']
    
    def update(self, instance, validated_data):
        instance.responded_at = timezone.now()
        return super().update(instance, validated_data)


class DocumentStatsSerializer(serializers.Serializer):
    total_documents = serializers.IntegerField()
    total_size = serializers.IntegerField()
    documents_by_category = serializers.DictField()
    documents_by_trust_level = serializers.DictField()
    recent_uploads = serializers.ListField()
    most_viewed = serializers.ListField()
    most_downloaded = serializers.ListField()


class DocumentSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False)
    category = serializers.IntegerField(required=False)
    trust_level = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)


class DocumentBulkActionSerializer(serializers.Serializer):
    document_ids = serializers.ListField(child=serializers.UUIDField())
    action = serializers.ChoiceField(choices=[
        ('delete', 'Delete'),
        ('archive', 'Archive'),
        ('share', 'Share'),
        ('download', 'Download'),
    ])
    target_user = serializers.IntegerField(required=False)  # For share action
    permission = serializers.CharField(required=False)  # For share action


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'version', 'file_size', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'version', 'file_size', 'created_at', 'updated_at']


class DocumentEncryptionSerializer(serializers.Serializer):
    encryption_key = serializers.CharField(write_only=True)
    encrypted_data = serializers.CharField()
    
    def validate_encryption_key(self, value):
        # Here you would validate the encryption key
        if len(value) < 32:
            raise serializers.ValidationError("Encryption key must be at least 32 characters") 