#!/usr/bin/env python3
"""
Docker setup test script for Neodocs
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Command failed: {command}")
            print(f"Error: {result.stderr}")
            return False
        return result
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def check_docker():
    """Check if Docker is running"""
    print("🔍 Checking Docker...")
    result = run_command("docker --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Docker is not installed or not running")
        return False

    print(f"✅ Docker version: {result.stdout.strip()}")
    return True


def check_docker_compose():
    """Check if Docker Compose is available"""
    print("🔍 Checking Docker Compose...")
    result = run_command("docker-compose --version", check=False)
    if not result or result.returncode != 0:
        print("❌ Docker Compose is not available")
        return False

    print(f"✅ Docker Compose version: {result.stdout.strip()}")
    return True


def check_env_file():
    """Check if .env file exists"""
    print("🔍 Checking environment file...")
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Run: python setup_env.py")
        return False

    print("✅ .env file found")
    return True


def check_services():
    """Check if all services are running"""
    print("🔍 Checking Docker services...")
    result = run_command("docker-compose ps", check=False)
    if not result or result.returncode != 0:
        print("❌ Failed to check services")
        return False

    print("📋 Service Status:")
    print(result.stdout)

    # Check if all services are up
    if "Up" not in result.stdout:
        print("❌ Some services are not running")
        return False

    return True


def test_api_endpoint():
    """Test the API endpoint"""
    print("🔍 Testing API endpoint...")
    try:
        response = requests.get("http://localhost:8000/api/v1/", timeout=10)
        if response.status_code == 200:
            print("✅ API is responding")
            return True
        else:
            print(f"⚠️  API responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {e}")
        return False


def test_database():
    """Test database connection"""
    print("🔍 Testing database connection...")
    result = run_command(
        "docker-compose exec -T db pg_isready -U neodocs_user -d neodocs_db",
        check=False,
    )
    if result and result.returncode == 0:
        print("✅ Database is ready")
        return True
    else:
        print("❌ Database is not ready")
        return False


def test_redis():
    """Test Redis connection"""
    print("🔍 Testing Redis connection...")
    result = run_command("docker-compose exec -T redis redis-cli ping", check=False)
    if result and "PONG" in result.stdout:
        print("✅ Redis is responding")
        return True
    else:
        print("❌ Redis is not responding")
        return False


def main():
    """Main test function"""
    print("🚀 Neodocs Docker Setup Test")
    print("=" * 40)

    tests = [
        ("Docker", check_docker),
        ("Docker Compose", check_docker_compose),
        ("Environment File", check_env_file),
        ("Docker Services", check_services),
        ("Database", test_database),
        ("Redis", test_redis),
        ("API Endpoint", test_api_endpoint),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your Docker setup is working correctly.")
        print("\n📋 Next steps:")
        print(
            "1. Create a superuser: docker-compose exec web python manage.py createsuperuser"
        )
        print("2. Access the API at: http://localhost:8000/api/v1/")
        print("3. View logs: docker-compose logs -f")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Docker is running")
        print("2. Run: docker-compose down && docker-compose up --build")
        print("3. Check logs: docker-compose logs")
        sys.exit(1)


if __name__ == "__main__":
    main()
