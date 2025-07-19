# Docker Deployment Guide

This guide covers how to deploy your Django OAuth application using Docker with PostgreSQL and Redis.

## 🐳 Docker Setup

### Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)
- At least 2GB of available RAM

### Quick Start

#### 1. Development Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd neocode-backend

# Start development environment
docker-compose -f docker-compose.dev.yml up --build
```

#### 2. Production Environment

```bash
# Start production environment
docker-compose up --build
```

## 📁 Docker Files Structure

```
neocode-backend/
├── Dockerfile                 # Main application container
├── docker-compose.yml         # Production services
├── docker-compose.dev.yml     # Development services
├── nginx.conf                 # Nginx configuration
├── env.production             # Production environment variables
├── requirements.txt           # Python dependencies
└── DOCKER_GUIDE.md           # This file
```

## 🚀 Services Overview

### Production Services (`docker-compose.yml`)

| Service | Port | Description |
|---------|------|-------------|
| `web` | 8000 | Django application (Gunicorn) |
| `db` | 5432 | PostgreSQL database |
| `redis` | 6379 | Redis cache/session storage |
| `nginx` | 80/443 | Nginx reverse proxy |

### Development Services (`docker-compose.dev.yml`)

| Service | Port | Description |
|---------|------|-------------|
| `web` | 8000 | Django application (Django dev server) |
| `db` | 5432 | PostgreSQL database |
| `redis` | 6379 | Redis cache/session storage |

## 🔧 Configuration

### Environment Variables

#### Development
```bash
# Use docker-compose.dev.yml which has development settings
DEBUG=True
CORS_ALLOW_ALL_ORIGINS=True
LOG_LEVEL=DEBUG
```

#### Production
```bash
# Use docker-compose.yml with production settings
DEBUG=False
CORS_ALLOW_ALL_ORIGINS=False
LOG_LEVEL=INFO
```

### Database Configuration

The application automatically detects PostgreSQL vs SQLite:

- **PostgreSQL**: `DATABASE_URL=postgresql://user:pass@host:port/db`
- **SQLite**: `DATABASE_URL=sqlite:///db.sqlite3`

### Redis Configuration

Redis is used for:
- Session storage
- Caching
- Rate limiting

Configuration: `REDIS_URL=redis://redis:6379/0`

## 🛠️ Commands

### Development

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Start in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop development environment
docker-compose -f docker-compose.dev.yml down

# Rebuild containers
docker-compose -f docker-compose.dev.yml up --build
```

### Production

```bash
# Start production environment
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop production environment
docker-compose down

# Rebuild containers
docker-compose up --build
```

### Database Operations

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access database shell
docker-compose exec db psql -U neodocs_user -d neodocs_db

# Backup database
docker-compose exec db pg_dump -U neodocs_user neodocs_db > backup.sql

# Restore database
docker-compose exec -T db psql -U neodocs_user -d neodocs_db < backup.sql
```

### Django Management

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create migrations
docker-compose exec web python manage.py makemigrations

# Run tests
docker-compose exec web python manage.py test

# Shell access
docker-compose exec web python manage.py shell
```

## 🔒 Security

### Production Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure proper CORS origins
- [ ] Use strong database passwords
- [ ] Enable security headers in Nginx
- [ ] Set up rate limiting
- [ ] Configure proper logging

### Environment Variables Security

```bash
# Generate a secure secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set environment variables
export SECRET_KEY="your-secure-secret-key"
export GOOGLE_OAUTH_CLIENT_ID="your-google-client-id"
export GOOGLE_OAUTH_CLIENT_SECRET="your-google-client-secret"
```

## 📊 Monitoring

### Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs db
docker-compose logs redis
docker-compose logs nginx

# Follow logs in real-time
docker-compose logs -f web
```

### Health Checks

```bash
# Check container status
docker-compose ps

# Check resource usage
docker stats

# Check database connectivity
docker-compose exec web python manage.py check --database default
```

## 🔄 Deployment Workflow

### 1. Initial Setup

```bash
# Clone repository
git clone <your-repo-url>
cd neocode-backend

# Create environment file
cp env.production .env

# Edit environment variables
nano .env

# Start services
docker-compose up --build
```

### 2. Database Setup

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load initial data (if any)
docker-compose exec web python manage.py loaddata initial_data.json
```

### 3. Static Files

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. SSL Setup (Production)

```bash
# Generate SSL certificates
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/nginx.key -out ssl/nginx.crt

# Update nginx.conf with SSL configuration
# Uncomment HTTPS server block in nginx.conf
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

#### 2. Redis Connection Error
```bash
# Check if Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Restart Redis
docker-compose restart redis
```

#### 3. Static Files Not Loading
```bash
# Rebuild static files
docker-compose exec web python manage.py collectstatic --noinput --clear

# Check nginx configuration
docker-compose exec nginx nginx -t
```

#### 4. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Rebuild containers
docker-compose down
docker-compose up --build
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_user_email ON auth_api_customuser(email);
CREATE INDEX idx_user_google_id ON auth_api_customuser(google_id);
```

#### 2. Redis Optimization
```bash
# Configure Redis for better performance
# Edit redis.conf in docker-compose.yml
```

#### 3. Nginx Optimization
```bash
# Enable gzip compression
# Configure worker processes
# Set up caching headers
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale web service
docker-compose up --scale web=3

# Use load balancer
# Configure nginx upstream with multiple web instances
```

### Vertical Scaling

```bash
# Increase memory limits in docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.4
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.KEY }}
          script: |
            cd /path/to/neocode-backend
            git pull origin main
            docker-compose down
            docker-compose up --build -d
            docker-compose exec web python manage.py migrate
            docker-compose exec web python manage.py collectstatic --noinput
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)
- [Nginx Docker Image](https://hub.docker.com/_/nginx)

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Ensure all services are running: `docker-compose ps`
4. Check network connectivity between containers
5. Verify database migrations are applied
6. Check file permissions and ownership 