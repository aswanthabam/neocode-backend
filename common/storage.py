"""
Common file storage utilities using Supabase
"""
import os
import uuid
from datetime import datetime
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
from supabase import create_client, Client
import mimetypes


class SupabaseStorage(Storage):
    """
    Custom storage class for Supabase file storage
    """
    
    def __init__(self, bucket_name='documents'):
        self.bucket_name = bucket_name
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_ANON_KEY
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def _open(self, name, mode='rb'):
        """Open a file from Supabase storage"""
        try:
            response = self.supabase.storage.from_(self.bucket_name).download(name)
            return ContentFile(response)
        except Exception as e:
            raise FileNotFoundError(f"File {name} not found in Supabase storage: {e}")
    
    def _save(self, name, content):
        """Save a file to Supabase storage"""
        try:
            # Generate unique filename if name is not provided
            if not name:
                ext = self._get_extension(content.name)
                name = f"{uuid.uuid4()}{ext}"
            
            # Upload file to Supabase
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=name,
                file=content.read(),
                file_options={"content-type": content.content_type}
            )
            
            return name
        except Exception as e:
            raise Exception(f"Failed to upload file to Supabase: {e}")
    
    def delete(self, name):
        """Delete a file from Supabase storage"""
        try:
            self.supabase.storage.from_(self.bucket_name).remove([name])
        except Exception as e:
            raise Exception(f"Failed to delete file from Supabase: {e}")
    
    def exists(self, name):
        """Check if a file exists in Supabase storage"""
        try:
            files = self.supabase.storage.from_(self.bucket_name).list(path=os.path.dirname(name))
            return name in [f['name'] for f in files]
        except:
            return False
    
    def url(self, name):
        """Get the public URL for a file"""
        try:
            return self.supabase.storage.from_(self.bucket_name).get_public_url(name)
        except Exception as e:
            raise Exception(f"Failed to get public URL: {e}")
    
    def size(self, name):
        """Get the size of a file"""
        try:
            files = self.supabase.storage.from_(self.bucket_name).list(path=os.path.dirname(name))
            for file in files:
                if file['name'] == os.path.basename(name):
                    return file.get('metadata', {}).get('size', 0)
            return 0
        except:
            return 0
    
    def _get_extension(self, filename):
        """Get file extension from filename"""
        if filename:
            return os.path.splitext(filename)[1]
        return ''
    
    def get_accessed_time(self, name):
        """Get the last accessed time of a file"""
        return datetime.now()
    
    def get_created_time(self, name):
        """Get the creation time of a file"""
        return datetime.now()
    
    def get_modified_time(self, name):
        """Get the last modified time of a file"""
        return datetime.now()


@deconstructible
class SupabaseFileField:
    """
    Common file field for Supabase storage
    """
    
    def __init__(self, bucket_name='documents', upload_to='', max_length=255):
        self.bucket_name = bucket_name
        self.upload_to = upload_to
        self.max_length = max_length
        self.storage = SupabaseStorage(bucket_name)
    
    def __call__(self, *args, **kwargs):
        return self
    
    def __eq__(self, other):
        return (
            isinstance(other, SupabaseFileField) and
            self.bucket_name == other.bucket_name and
            self.upload_to == other.upload_to and
            self.max_length == other.max_length
        )
    
    def __hash__(self):
        return hash((self.bucket_name, self.upload_to, self.max_length))
    
    def __str__(self):
        return f"SupabaseFileField(bucket='{self.bucket_name}', upload_to='{self.upload_to}')"
    
    def __repr__(self):
        return self.__str__()


def get_supabase_client():
    """Get Supabase client instance"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def upload_file_to_supabase(file, bucket_name='documents', path=None):
    """
    Upload a file to Supabase storage
    
    Args:
        file: File object to upload
        bucket_name: Supabase bucket name
        path: Optional path within the bucket
    
    Returns:
        dict: Upload response with file information
    """
    try:
        supabase = get_supabase_client()
        
        # Generate unique filename if path not provided
        if not path:
            ext = os.path.splitext(file.name)[1] if file.name else ''
            filename = f"{uuid.uuid4()}{ext}"
        else:
            filename = path
        
        # Upload file
        response = supabase.storage.from_(bucket_name).upload(
            path=filename,
            file=file.read(),
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
        
        return {
            'success': True,
            'filename': filename,
            'public_url': public_url,
            'size': file.size,
            'content_type': file.content_type
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def delete_file_from_supabase(filename, bucket_name='documents'):
    """
    Delete a file from Supabase storage
    
    Args:
        filename: Name of the file to delete
        bucket_name: Supabase bucket name
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        supabase.storage.from_(bucket_name).remove([filename])
        return True
    except Exception as e:
        print(f"Error deleting file {filename}: {e}")
        return False


def get_file_url(filename, bucket_name='documents'):
    """
    Get public URL for a file
    
    Args:
        filename: Name of the file
        bucket_name: Supabase bucket name
    
    Returns:
        str: Public URL of the file
    """
    try:
        supabase = get_supabase_client()
        return supabase.storage.from_(bucket_name).get_public_url(filename)
    except Exception as e:
        print(f"Error getting file URL for {filename}: {e}")
        return None 