#!/usr/bin/env python3
"""
Setup script for Neodocs environment configuration
"""
import os
import secrets
import string
from pathlib import Path


def generate_secret_key(length=50):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    example_file = Path("env.example")

    if env_file.exists():
        print("⚠️  .env file already exists. Skipping creation.")
        return

    if not example_file.exists():
        print("❌ env.example file not found!")
        return

    # Read the example file
    with open(example_file, "r") as f:
        content = f.read()

    # Replace placeholder values
    content = content.replace(
        "django-insecure-njee6zl+-^-pguefna_5wvq-xyytdm&&sm(%4n9j&_23(q0%+s",
        generate_secret_key(),
    )

    # Write the .env file
    with open(env_file, "w") as f:
        f.write(content)

    print("✅ .env file created successfully!")
    print("📝 Please update the .env file with your actual configuration values.")


def main():
    """Main setup function"""
    print("🚀 Neodocs Environment Setup")
    print("=" * 40)

    # Create .env file
    create_env_file()

    print("\n📋 Next steps:")
    print("1. Update the .env file with your actual configuration")
    print("2. For development: docker-compose -f docker-compose.dev.yml up --build")
    print("3. For production: docker-compose up --build")
    print("\n🔧 Required environment variables to configure:")
    print("   - SECRET_KEY (auto-generated)")
    print("   - GOOGLE_OAUTH_CLIENT_ID")
    print("   - GOOGLE_OAUTH_CLIENT_SECRET")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_ANON_KEY")
    print("   - SUPABASE_SERVICE_ROLE_KEY")
    print("   - EMAIL_HOST_USER")
    print("   - EMAIL_HOST_PASSWORD")


if __name__ == "__main__":
    main()
