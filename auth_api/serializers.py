from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, OAuthToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'full_name', 'email', 'username', 'password', 'password_confirm')
        extra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': True},
            'username': {'required': False}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username', validated_data['email']),
            full_name=validated_data['full_name'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'full_name', 'email', 'username', 'profile_picture', 'is_oauth_user', 'created_at', 'last_login')
        read_only_fields = ('id', 'created_at', 'last_login')


class GoogleOAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    
    def validate_access_token(self, value):
        # This will be validated in the view
        return value


class OAuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthToken
        fields = ('access_token', 'refresh_token', 'token_type', 'expires_at', 'created_at')
        read_only_fields = ('created_at',) 