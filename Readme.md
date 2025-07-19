# Django OAuth Authentication Backend

A comprehensive Django backend with OAuth authentication system including user registration, login, and Google OAuth integration.

## Features

- ✅ **User Registration**: Full name, email, and password registration
- ✅ **User Login**: Email and password authentication
- ✅ **Google OAuth**: Complete Google OAuth integration
- ✅ **JWT Authentication**: Secure token-based authentication
- ✅ **User Profile Management**: Get and update user profiles
- ✅ **Token Management**: Refresh and logout functionality
- ✅ **Custom User Model**: Extended user model with OAuth support
- ✅ **REST API**: Clean RESTful API endpoints
- ✅ **CORS Support**: Cross-origin resource sharing enabled
- ✅ **Admin Interface**: Django admin integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 4. Run the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/auth/`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | User registration |
| POST | `/api/auth/login/` | User login |
| POST | `/api/auth/google/` | Google OAuth authentication |
| GET | `/api/auth/google/url/` | Get Google OAuth URL |
| GET | `/api/auth/profile/` | Get user profile |
| PUT | `/api/auth/profile/` | Update user profile |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | User logout |

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Set authorized redirect URIs to: `http://localhost:8000/api/auth/google/callback/`
6. Copy Client ID and Client Secret
7. Set environment variables:

```bash
# Windows
set GOOGLE_OAUTH_CLIENT_ID=your_client_id
set GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
set GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/google/callback/

# Linux/Mac
export GOOGLE_OAUTH_CLIENT_ID=your_client_id
export GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
export GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/google/callback/
```

## Testing the API

Run the test script to verify all endpoints:

```bash
python test_api.py
```

## Example Usage

### User Registration

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

### User Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Get User Profile

```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Project Structure

```
neocode-backend/
├── auth_api/                 # Authentication app
│   ├── models.py            # Custom user and OAuth models
│   ├── serializers.py       # API serializers
│   ├── views.py             # API views
│   ├── urls.py              # URL patterns
│   ├── admin.py             # Admin configuration
│   └── managers.py          # Custom user manager
├── neodocs/                 # Main project
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── requirements.txt          # Python dependencies
├── API_DOCUMENTATION.md     # Detailed API documentation
├── test_api.py              # API test script
└── README.md                # This file
```

## Database Models

### CustomUser
- `email`: Primary identifier (unique)
- `full_name`: User's full name
- `username`: Optional username (unique)
- `password`: Hashed password (null for OAuth users)
- `google_id`: Google OAuth ID (unique)
- `profile_picture`: URL to profile picture
- `is_oauth_user`: Boolean flag for OAuth users
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp
- `last_login`: Last login timestamp

### OAuthToken
- `user`: Foreign key to CustomUser
- `access_token`: OAuth access token
- `refresh_token`: OAuth refresh token
- `token_type`: Token type (default: Bearer)
- `expires_at`: Token expiration timestamp
- `created_at`: Token creation timestamp

## Authentication Flow

### Regular Authentication
1. User registers with email/password
2. User logs in with email/password
3. Server returns JWT access and refresh tokens
4. Client includes access token in Authorization header
5. Use refresh token to get new access token when expired

### Google OAuth Flow
1. Client gets Google OAuth URL from `/api/auth/google/url/`
2. User is redirected to Google for authentication
3. Google returns access token to client
4. Client sends access token to `/api/auth/google/`
5. Server verifies token with Google and creates/updates user
6. Server returns JWT tokens for subsequent requests

## Security Features

- JWT token-based authentication
- Password hashing with Django's built-in hashers
- CORS configuration for cross-origin requests
- Token blacklisting on logout
- Secure password validation
- OAuth token verification with Google

## Development

### Adding New OAuth Providers

1. Add new fields to `CustomUser` model
2. Create new OAuth view similar to `GoogleOAuthView`
3. Add URL patterns
4. Update serializers if needed

### Customizing User Model

The `CustomUser` model can be extended with additional fields:

```python
class CustomUser(AbstractUser):
    # Add your custom fields here
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    # ... other fields
```

## Production Deployment

1. Set `DEBUG = False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set secure `SECRET_KEY`
4. Configure proper CORS settings
5. Set up environment variables for OAuth credentials
6. Use HTTPS in production
7. Configure proper logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
