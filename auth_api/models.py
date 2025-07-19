from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    objects = CustomUserManager()
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    
    # OAuth fields
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    profile_picture = models.URLField(blank=True, null=True)
    is_oauth_user = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'username']
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class OAuthToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_type = models.CharField(max_length=50, default='Bearer')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Token for {self.user.email}"
    
    class Meta:
        verbose_name = 'OAuth Token'
        verbose_name_plural = 'OAuth Tokens'
