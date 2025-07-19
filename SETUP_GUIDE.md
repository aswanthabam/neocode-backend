# Environment Setup Guide

## Quick Start

### 1. Create Environment File

Run the setup script to create your `.env` file:

```bash
python setup_env.py
```

Or manually copy the example file:

```bash
cp env.example .env
```

### 2. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Set authorized redirect URIs to: `http://localhost:8000/api/auth/google/callback/`
6. Copy Client ID and Client Secret
7. Update your `.env` file:

```env
GOOGLE_OAUTH_CLIENT_ID=your_actual_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_actual_client_secret_here
```

### 3. Generate Secret Key

Generate a new Django secret key:

```bash
python setup_env.py
# Choose option 2: Generate new secret key
```

Or manually update the SECRET_KEY in your `.env` file.

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Start the Server

```bash
python manage.py runserver
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Debug mode | `True` (dev), `False` (prod) |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth Client ID | `123456789-...` |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth Client Secret | `GOCSPX-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `JWT_ACCESS_TOKEN_LIFETIME` | Access token lifetime (minutes) | `60` |
| `JWT_REFRESH_TOKEN_LIFETIME` | Refresh token lifetime (days) | `1` |
| `CORS_ALLOW_ALL_ORIGINS` | Allow all CORS origins | `True` |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_HOST_USER` | Email username | `` |
| `EMAIL_HOST_PASSWORD` | Email password | `` |

### Production Variables

| Variable | Description | Production Value |
|----------|-------------|------------------|
| `DEBUG` | Debug mode | `False` |
| `SECURE_SSL_REDIRECT` | Redirect to HTTPS | `True` |
| `SECURE_HSTS_SECONDS` | HSTS header duration | `31536000` |
| `SESSION_COOKIE_SECURE` | Secure session cookies | `True` |
| `CSRF_COOKIE_SECURE` | Secure CSRF cookies | `True` |
| `CORS_ALLOW_ALL_ORIGINS` | Allow all CORS origins | `False` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins | `https://yourdomain.com` |

## Testing

Test your setup:

```bash
python test_api.py
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'decouple'**
   ```bash
   pip install python-decouple
   ```

2. **Google OAuth not working**
   - Check your Client ID and Secret are correct
   - Verify redirect URI matches exactly
   - Ensure Google+ API is enabled

3. **CORS errors**
   - Update `CORS_ALLOWED_ORIGINS` with your frontend URL
   - Or set `CORS_ALLOW_ALL_ORIGINS=True` for development

4. **Database errors**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Environment File Structure

Your `.env` file should look like this:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/google/callback/

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1

# CORS Settings
CORS_ALLOW_ALL_ORIGINS=True

# Email Settings (Optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Security Notes

1. **Never commit `.env` file to version control**
2. **Use different secrets for development and production**
3. **Rotate secrets regularly in production**
4. **Use HTTPS in production**
5. **Set appropriate CORS origins for production** 