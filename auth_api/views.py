from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
import requests
import json
from datetime import datetime, timedelta

from .models import CustomUser, OAuthToken
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    GoogleOAuthSerializer,
    OAuthTokenSerializer
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User registered successfully',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Update last login
            user.last_login = datetime.now()
            user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleOAuthView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = GoogleOAuthSerializer(data=request.data)
        if serializer.is_valid():
            access_token = serializer.validated_data['access_token']
            
            # Verify token with Google
            google_user_info = self.get_google_user_info(access_token)
            if not google_user_info:
                return Response({'error': 'Invalid Google token'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create user
            user = self.get_or_create_google_user(google_user_info)
            
            # Update last login
            user.last_login = datetime.now()
            user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Google OAuth login successful',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_google_user_info(self, access_token):
        """Get user info from Google using access token"""
        try:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting Google user info: {e}")
            return None
    
    def get_or_create_google_user(self, google_user_info):
        """Get or create user from Google OAuth data"""
        google_id = google_user_info.get('id')
        email = google_user_info.get('email')
        full_name = google_user_info.get('name', '')
        profile_picture = google_user_info.get('picture', '')
        
        # Try to find existing user by Google ID or email
        user = None
        if google_id:
            try:
                user = CustomUser.objects.get(google_id=google_id)
            except CustomUser.DoesNotExist:
                pass
        
        if not user and email:
            try:
                user = CustomUser.objects.get(email=email)
                # Update with Google ID if not already set
                if not user.google_id:
                    user.google_id = google_id
                    user.is_oauth_user = True
                    user.save()
            except CustomUser.DoesNotExist:
                pass
        
        # Create new user if not found
        if not user:
            username = email.split('@')[0] if email else f"user_{google_id}"
            # Ensure username is unique
            counter = 1
            original_username = username
            while CustomUser.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1
            
            user = CustomUser.objects.create_user(
                email=email,
                username=username,
                full_name=full_name,
                google_id=google_id,
                profile_picture=profile_picture,
                is_oauth_user=True,
                password=None  # OAuth users don't need password
            )
        
        return user


class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as token_error:
                    # If blacklisting fails, still return success (token might be expired)
                    print(f"Token blacklist error: {token_error}")
                    # Continue with logout even if blacklisting fails
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Logout error: {e}")
            # Return success even if there's an error, as the user is still logged out
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def google_oauth_url(request):
    """Get Google OAuth URL for frontend"""
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
    scope = 'email profile'
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&access_type=offline"
    
    return Response({
        'auth_url': auth_url,
        'client_id': client_id,
        'redirect_uri': redirect_uri
    })
