#!/usr/bin/env python3
"""
Environment Setup Script for Django OAuth Project
This script helps you create a .env file from env.example
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from env.example"""
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    # Check if env.example exists
    if not os.path.exists('env.example'):
        print("❌ env.example file not found!")
        return
    
    try:
        # Copy env.example to .env
        shutil.copy('env.example', '.env')
        print("✅ .env file created successfully!")
        print("\n📝 Next steps:")
        print("1. Edit .env file with your actual values")
        print("2. Set up Google OAuth credentials:")
        print("   - Go to https://console.cloud.google.com/")
        print("   - Create OAuth 2.0 credentials")
        print("   - Update GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET")
        print("3. Run: python manage.py migrate")
        print("4. Run: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

def generate_secret_key():
    """Generate a new Django secret key"""
    from django.core.management.utils import get_random_secret_key
    return get_random_secret_key()

def update_env_with_secret():
    """Update .env file with a new secret key"""
    if not os.path.exists('.env'):
        print("❌ .env file not found! Run setup first.")
        return
    
    try:
        # Read current .env file
        with open('.env', 'r') as f:
            content = f.read()
        
        # Generate new secret key
        new_secret = generate_secret_key()
        
        # Replace the secret key
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('SECRET_KEY='):
                lines[i] = f'SECRET_KEY={new_secret}'
                break
        
        # Write back to file
        with open('.env', 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ Secret key updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating secret key: {e}")

def show_env_help():
    """Show help for environment variables"""
    print("\n📋 Environment Variables Guide:")
    print("=" * 50)
    
    print("\n🔐 Required for OAuth:")
    print("GOOGLE_OAUTH_CLIENT_ID - Your Google OAuth Client ID")
    print("GOOGLE_OAUTH_CLIENT_SECRET - Your Google OAuth Client Secret")
    
    print("\n⚙️  Development Settings:")
    print("DEBUG - Set to True for development, False for production")
    print("SECRET_KEY - Django secret key (auto-generated)")
    print("ALLOWED_HOSTS - Comma-separated list of allowed hosts")
    
    print("\n📧 Email Settings (Optional):")
    print("EMAIL_HOST - SMTP server (e.g., smtp.gmail.com)")
    print("EMAIL_PORT - SMTP port (usually 587)")
    print("EMAIL_HOST_USER - Your email address")
    print("EMAIL_HOST_PASSWORD - Your email password or app password")
    
    print("\n🔒 Security Settings (Production):")
    print("SECURE_SSL_REDIRECT - Redirect to HTTPS")
    print("SECURE_HSTS_SECONDS - HSTS header duration")
    print("SESSION_COOKIE_SECURE - Secure session cookies")
    print("CSRF_COOKIE_SECURE - Secure CSRF cookies")
    
    print("\n📊 JWT Settings:")
    print("JWT_ACCESS_TOKEN_LIFETIME - Access token lifetime in minutes")
    print("JWT_REFRESH_TOKEN_LIFETIME - Refresh token lifetime in days")
    
    print("\n🌐 CORS Settings:")
    print("CORS_ALLOW_ALL_ORIGINS - Allow all origins (development)")
    print("CORS_ALLOWED_ORIGINS - Comma-separated list of allowed origins")

def main():
    """Main function"""
    print("🚀 Django OAuth Environment Setup")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Create .env file from env.example")
        print("2. Generate new secret key")
        print("3. Show environment variables help")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            create_env_file()
        elif choice == '2':
            update_env_with_secret()
        elif choice == '3':
            show_env_help()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 