# Django OAuth Authentication API Documentation

This Django backend provides a comprehensive OAuth authentication system with REST APIs for user registration, login, and Google OAuth integration.

## Features

- ✅ User registration with full name, email, and password
- ✅ User login with email and password
- ✅ Google OAuth authentication
- ✅ JWT token-based authentication
- ✅ User profile management
- ✅ Token refresh and logout functionality
- ✅ Custom user model with OAuth support

## API Endpoints

### Base URL
```
http://localhost:8000/api/auth/
```

### 1. User Registration
**POST** `/register/`

Register a new user with email, password, and full name.

**Request Body:**
```json
{
    "full_name": "John Doe",
    "email": "john@example.com",
    "username": "johndoe",  // Optional, defaults to email
    "password": "securepassword123",
    "password_confirm": "securepassword123"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "username": "johndoe",
        "profile_picture": null,
        "is_oauth_user": false,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-01T00:00:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 2. User Login
**POST** `/login/`

Login with email and password.

**Request Body:**
```json
{
    "email": "john@example.com",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "username": "johndoe",
        "profile_picture": null,
        "is_oauth_user": false,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-01T12:00:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 3. Google OAuth Authentication
**POST** `/google/`

Authenticate using Google OAuth access token.

**Request Body:**
```json
{
    "access_token": "google_access_token_here"
}
```

**Response (200 OK):**
```json
{
    "message": "Google OAuth login successful",
    "user": {
        "id": 2,
        "full_name": "Jane Smith",
        "email": "jane@gmail.com",
        "username": "jane",
        "profile_picture": "https://lh3.googleusercontent.com/...",
        "is_oauth_user": true,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-01T12:00:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 4. Get Google OAuth URL
**GET** `/google/url/`

Get the Google OAuth URL for frontend integration.

**Response (200 OK):**
```json
{
    "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
    "client_id": "your-google-client-id",
    "redirect_uri": "http://localhost:8000/api/auth/google/callback/"
}
```

### 5. User Profile
**GET** `/profile/`

Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "username": "johndoe",
    "profile_picture": null,
    "is_oauth_user": false,
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T12:00:00Z"
}
```

**PUT** `/profile/`

Update user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "full_name": "John Updated Doe",
    "username": "johnupdated"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "full_name": "John Updated Doe",
    "email": "john@example.com",
    "username": "johnupdated",
    "profile_picture": null,
    "is_oauth_user": false,
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T12:00:00Z"
}
```

### 6. Token Refresh
**POST** `/token/refresh/`

Refresh access token using refresh token.

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 7. Logout
**POST** `/logout/`

Logout and blacklist refresh token (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "message": "Logout successful"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "email": ["This field is required."],
    "password": ["This field is required."]
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

## Authentication

All protected endpoints require a valid JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Set authorized redirect URIs to: `http://localhost:8000/api/auth/google/callback/`
6. Copy Client ID and Client Secret
7. Set environment variables:
   ```bash
   GOOGLE_OAUTH_CLIENT_ID=your_client_id
   GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
   GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/auth/google/callback/
   ```

## Frontend Integration

### Google OAuth Flow
1. Call `GET /api/auth/google/url/` to get the OAuth URL
2. Redirect user to the returned `auth_url`
3. Handle the callback and get the access token from Google
4. Send the access token to `POST /api/auth/google/` to authenticate

### Regular Authentication
1. Use `POST /api/auth/register/` for new users
2. Use `POST /api/auth/login/` for existing users
3. Store the returned tokens securely
4. Include the access token in Authorization header for protected requests
5. Use `POST /api/auth/token/refresh/` to refresh expired tokens

## Running the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/auth/`

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