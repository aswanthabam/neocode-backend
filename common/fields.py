"""
Common file fields for Supabase storage
"""
import os
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.conf import settings
from .storage import upload_file_to_supabase, delete_file_from_supabase


class SupabaseFileField(models.FileField):
    """
    Custom file field for Supabase storage with validation
    """
    
    def __init__(self, bucket_name='documents', allowed_types=None, max_size=None, *args, **kwargs):
        self.bucket_name = bucket_name
        self.allowed_types = allowed_types or getattr(settings, 'ALLOWED_FILE_TYPES', [])
        self.max_size = max_size or getattr(settings, 'MAX_FILE_SIZE', 10 * 1024 * 1024)  # 10MB
        super().__init__(*args, **kwargs)
    
    def clean(self, value, model_instance):
        """Validate file before saving"""
        if value:
            # Check file size
            if value.size > self.max_size:
                raise ValidationError(f'File size must be under {self.max_size / (1024*1024):.1f}MB')
            
            # Check file type
            file_ext = os.path.splitext(value.name)[1].lower().lstrip('.')
            if file_ext not in self.allowed_types:
                raise ValidationError(f'File type {file_ext} is not allowed. Allowed types: {", ".join(self.allowed_types)}')
        
        return super().clean(value, model_instance)
    
    def save_form_data(self, instance, data):
        """Handle file upload to Supabase"""
        if data and hasattr(data, 'read'):
            # Upload to Supabase
            result = upload_file_to_supabase(data, self.bucket_name)
            if result['success']:
                # Save the filename to the database
                setattr(instance, self.name, result['filename'])
            else:
                raise ValidationError(f"Failed to upload file: {result.get('error', 'Unknown error')}")
        else:
            super().save_form_data(instance, data)
    
    def pre_save(self, model_instance, add):
        """Handle file before saving to database"""
        file = getattr(model_instance, self.attname)
        if file and hasattr(file, 'read'):
            # Upload to Supabase
            result = upload_file_to_supabase(file, self.bucket_name)
            if result['success']:
                # Return the filename for database storage
                return result['filename']
            else:
                raise ValidationError(f"Failed to upload file: {result.get('error', 'Unknown error')}")
        return file
    
    def delete_file(self, instance):
        """Delete file from Supabase when model is deleted"""
        filename = getattr(instance, self.name)
        if filename:
            delete_file_from_supabase(filename, self.bucket_name)


class SupabaseImageField(models.ImageField):
    """
    Custom image field for Supabase storage with validation
    """
    
    def __init__(self, bucket_name='images', allowed_types=None, max_size=None, *args, **kwargs):
        self.bucket_name = bucket_name
        self.allowed_types = allowed_types or getattr(settings, 'ALLOWED_IMAGE_TYPES', [])
        self.max_size = max_size or getattr(settings, 'MAX_FILE_SIZE', 5 * 1024 * 1024)  # 5MB
        super().__init__(*args, **kwargs)
    
    def clean(self, value, model_instance):
        """Validate image before saving"""
        if value:
            # Check file size
            if value.size > self.max_size:
                raise ValidationError(f'Image size must be under {self.max_size / (1024*1024):.1f}MB')
            
            # Check file type
            file_ext = os.path.splitext(value.name)[1].lower().lstrip('.')
            if file_ext not in self.allowed_types:
                raise ValidationError(f'Image type {file_ext} is not allowed. Allowed types: {", ".join(self.allowed_types)}')
        
        return super().clean(value, model_instance)
    
    def save_form_data(self, instance, data):
        """Handle image upload to Supabase"""
        if data and hasattr(data, 'read'):
            # Upload to Supabase
            result = upload_file_to_supabase(data, self.bucket_name)
            if result['success']:
                # Save the filename to the database
                setattr(instance, self.name, result['filename'])
            else:
                raise ValidationError(f"Failed to upload image: {result.get('error', 'Unknown error')}")
        else:
            super().save_form_data(instance, data)
    
    def pre_save(self, model_instance, add):
        """Handle image before saving to database"""
        image = getattr(model_instance, self.attname)
        if image and hasattr(image, 'read'):
            # Upload to Supabase
            result = upload_file_to_supabase(image, self.bucket_name)
            if result['success']:
                # Return the filename for database storage
                return result['filename']
            else:
                raise ValidationError(f"Failed to upload image: {result.get('error', 'Unknown error')}")
        return image
    
    def delete_file(self, instance):
        """Delete image from Supabase when model is deleted"""
        filename = getattr(instance, self.name)
        if filename:
            delete_file_from_supabase(filename, self.bucket_name)


class DocumentFileField(SupabaseFileField):
    """
    Specialized file field for documents
    """
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('bucket_name', 'documents')
        kwargs.setdefault('allowed_types', ['pdf', 'doc', 'docx', 'txt', 'rtf'])
        kwargs.setdefault('max_size', 50 * 1024 * 1024)  # 50MB for documents
        super().__init__(*args, **kwargs)


class ProfileImageField(SupabaseImageField):
    """
    Specialized image field for profile pictures
    """
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('bucket_name', 'profile-images')
        kwargs.setdefault('allowed_types', ['jpg', 'jpeg', 'png', 'webp'])
        kwargs.setdefault('max_size', 2 * 1024 * 1024)  # 2MB for profile images
        super().__init__(*args, **kwargs)


class QRCodeImageField(SupabaseImageField):
    """
    Specialized image field for QR codes
    """
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('bucket_name', 'qr-codes')
        kwargs.setdefault('allowed_types', ['png', 'jpg', 'jpeg'])
        kwargs.setdefault('max_size', 1 * 1024 * 1024)  # 1MB for QR codes
        super().__init__(*args, **kwargs) 