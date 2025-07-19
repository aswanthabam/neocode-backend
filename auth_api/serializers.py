from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Organization, OAuthToken, UserActivity


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'username', 'password', 'password_confirm', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'full_name', 'email', 'username', 'vault_id', 'user_type',
            'phone_number', 'date_of_birth', 'address', 'profile_picture',
            'is_verified', 'notification_preferences', 'privacy_settings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'vault_id', 'is_verified', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'username', 'phone_number', 'date_of_birth', 
            'address', 'notification_preferences', 'privacy_settings'
        ]
    
    def validate_username(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(id=user.id).filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value


class OrganizationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'user', 'user_email', 'user_full_name', 'name', 'description',
            'organization_type', 'website', 'email', 'phone', 'address',
            'is_verified', 'verification_date', 'can_issue_documents',
            'can_request_documents', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_verified', 'verification_date', 'created_at', 'updated_at']


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'name', 'description', 'organization_type', 'website', 'email',
            'phone', 'address', 'can_issue_documents', 'can_request_documents'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OrganizationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'name', 'description', 'organization_type', 'website', 'email',
            'phone', 'address', 'can_issue_documents', 'can_request_documents'
        ]


class GoogleOAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    
    def validate_access_token(self, value):
        # Here you would validate the Google access token
        # For now, we'll just return the value
        return value


class OAuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthToken
        fields = ['access_token', 'refresh_token', 'token_type', 'expires_at', 'created_at']
        read_only_fields = ['created_at']


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ['activity_type', 'description', 'ip_address', 'user_agent', 'metadata', 'created_at']
        read_only_fields = ['ip_address', 'user_agent', 'created_at']


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


class UserStatsSerializer(serializers.Serializer):
    total_documents = serializers.IntegerField()
    shared_documents = serializers.IntegerField()
    received_documents = serializers.IntegerField()
    pending_requests = serializers.IntegerField()
    qr_shares_created = serializers.IntegerField()
    last_activity = serializers.DateTimeField()


class NotificationPreferencesSerializer(serializers.Serializer):
    email_notifications = serializers.BooleanField(default=True)
    push_notifications = serializers.BooleanField(default=True)
    document_shared = serializers.BooleanField(default=True)
    document_requested = serializers.BooleanField(default=True)
    request_responded = serializers.BooleanField(default=True)
    qr_accessed = serializers.BooleanField(default=True)


class PrivacySettingsSerializer(serializers.Serializer):
    profile_visibility = serializers.ChoiceField(choices=[
        ('public', 'Public'),
        ('private', 'Private'),
        ('friends', 'Friends Only')
    ], default='private')
    show_email = serializers.BooleanField(default=False)
    show_phone = serializers.BooleanField(default=False)
    allow_document_requests = serializers.BooleanField(default=True)
    allow_qr_sharing = serializers.BooleanField(default=True) 