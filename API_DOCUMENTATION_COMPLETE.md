# Complete API Documentation

## 🚀 Overview

This document provides comprehensive documentation for the Document Vault API, a secure document management and sharing system with OAuth2 authentication, QR code sharing, and organization support.

## 📋 Table of Contents

1. [Authentication & User Management](#authentication--user-management)
2. [Document Management](#document-management)
3. [Document Sharing & Requests](#document-sharing--requests)
4. [QR Code Sharing](#qr-code-sharing)
5. [Organization Management](#organization-management)
6. [OAuth2 Token Management](#oauth2-token-management)
7. [API Documentation](#api-documentation)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)

---

## 🔐 Authentication & User Management

### User Registration
**Endpoint:** `POST /api/v1/auth/register/`

**Description:** Create a new user account with email and password

**Request Body:**
```json
{
    "full_name": "John Doe",
    "email": "john@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "user_type": "individual"
}
```

**Response (201):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "username": "johndoe",
        "vault_id": "johndoe@vault",
        "user_type": "individual",
        "is_verified": false,
        "created_at": "2025-07-20T00:00:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### User Login
**Endpoint:** `POST /api/v1/auth/login/`

**Description:** Authenticate user with email and password

**Request Body:**
```json
{
    "email": "john@example.com",
    "password": "securepassword123"
}
```

**Response (200):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "username": "johndoe",
        "vault_id": "johndoe@vault",
        "user_type": "individual",
        "is_verified": false,
        "created_at": "2025-07-20T00:00:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### Get User Profile
**Endpoint:** `GET /api/v1/auth/profile/`

**Description:** Retrieve current user's profile information

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "username": "johndoe",
    "vault_id": "johndoe@vault",
    "user_type": "individual",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-01",
    "address": "123 Main St, City, State",
    "profile_picture": "https://example.com/profile.jpg",
    "is_verified": false,
    "notification_preferences": {
        "email_notifications": true,
        "push_notifications": true
    },
    "privacy_settings": {
        "profile_visibility": "private",
        "show_email": false
    },
    "created_at": "2025-07-20T00:00:00Z",
    "updated_at": "2025-07-20T00:00:00Z"
}
```

### Update User Profile
**Endpoint:** `PUT /api/v1/auth/profile/`

**Description:** Update current user's profile details

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "full_name": "John Smith",
    "username": "johnsmith",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-01",
    "address": "456 Oak St, City, State",
    "notification_preferences": {
        "email_notifications": true,
        "push_notifications": false
    },
    "privacy_settings": {
        "profile_visibility": "public",
        "show_email": true
    }
}
```

### Token Refresh
**Endpoint:** `POST /api/v1/auth/token/refresh/`

**Description:** Refresh access token using refresh token

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### User Logout
**Endpoint:** `POST /api/v1/auth/logout/`

**Description:** Logout user and blacklist refresh token

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200):**
```json
{
    "message": "Logout successful"
}
```

### Password Change
**Endpoint:** `POST /api/v1/auth/password/change/`

**Description:** Change user password

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "old_password": "oldpassword123",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
}
```

### User Statistics
**Endpoint:** `GET /api/v1/auth/stats/`

**Description:** Get user statistics and activity summary

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "total_documents": 15,
    "shared_documents": 8,
    "received_documents": 5,
    "pending_requests": 2,
    "qr_shares_created": 12,
    "last_activity": "2025-07-20T10:30:00Z"
}
```

### Notification Preferences
**Endpoint:** `GET /api/v1/auth/notifications/preferences/`

**Description:** Get user notification preferences

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "email_notifications": true,
    "push_notifications": true,
    "document_shared": true,
    "document_requested": true,
    "request_responded": true,
    "qr_accessed": true
}
```

### Update Notification Preferences
**Endpoint:** `PUT /api/v1/auth/notifications/preferences/`

**Description:** Update user notification preferences

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "email_notifications": true,
    "push_notifications": false,
    "document_shared": true,
    "document_requested": false,
    "request_responded": true,
    "qr_accessed": true
}
```

### Privacy Settings
**Endpoint:** `GET /api/v1/auth/privacy/settings/`

**Description:** Get user privacy settings

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "profile_visibility": "private",
    "show_email": false,
    "show_phone": false,
    "allow_document_requests": true,
    "allow_qr_sharing": true
}
```

### Update Privacy Settings
**Endpoint:** `PUT /api/v1/auth/privacy/settings/`

**Description:** Update user privacy settings

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "profile_visibility": "public",
    "show_email": true,
    "show_phone": false,
    "allow_document_requests": true,
    "allow_qr_sharing": false
}
```

### User Activities
**Endpoint:** `GET /api/v1/auth/activities/`

**Description:** Get list of user activities

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `activity_type`: Filter by activity type
- `created_at`: Filter by creation date

**Response (200):**
```json
{
    "count": 25,
    "next": "http://api.example.com/api/v1/auth/activities/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "activity_type": "login",
            "description": "User logged in from 192.168.1.1",
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0...",
            "metadata": {},
            "created_at": "2025-07-20T10:30:00Z"
        }
    ]
}
```

---

## 🏢 Organization Management

### Create Organization Profile
**Endpoint:** `POST /api/v1/auth/organization/`

**Description:** Create organization profile for issuer/requester users

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "name": "Acme Corporation",
    "description": "A leading technology company",
    "organization_type": "corporate",
    "website": "https://acme.com",
    "email": "contact@acme.com",
    "phone": "+1234567890",
    "address": "123 Business St, City, State",
    "can_issue_documents": true,
    "can_request_documents": true
}
```

**Response (201):**
```json
{
    "id": 1,
    "user": 1,
    "user_email": "john@example.com",
    "user_full_name": "John Doe",
    "name": "Acme Corporation",
    "description": "A leading technology company",
    "organization_type": "corporate",
    "website": "https://acme.com",
    "email": "contact@acme.com",
    "phone": "+1234567890",
    "address": "123 Business St, City, State",
    "is_verified": false,
    "verification_date": null,
    "can_issue_documents": true,
    "can_request_documents": true,
    "created_at": "2025-07-20T00:00:00Z",
    "updated_at": "2025-07-20T00:00:00Z"
}
```

### Get Organization Profile
**Endpoint:** `GET /api/v1/auth/organization/`

**Description:** Retrieve organization profile information

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "id": 1,
    "user": 1,
    "user_email": "john@example.com",
    "user_full_name": "John Doe",
    "name": "Acme Corporation",
    "description": "A leading technology company",
    "organization_type": "corporate",
    "website": "https://acme.com",
    "email": "contact@acme.com",
    "phone": "+1234567890",
    "address": "123 Business St, City, State",
    "is_verified": true,
    "verification_date": "2025-07-20T00:00:00Z",
    "can_issue_documents": true,
    "can_request_documents": true,
    "created_at": "2025-07-20T00:00:00Z",
    "updated_at": "2025-07-20T00:00:00Z"
}
```

### Update Organization Profile
**Endpoint:** `PUT /api/v1/auth/organization/`

**Description:** Update organization profile details

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "name": "Acme Corporation Ltd",
    "description": "A leading technology company with global presence",
    "organization_type": "corporate",
    "website": "https://acme.com",
    "email": "info@acme.com",
    "phone": "+1234567890",
    "address": "456 Corporate Ave, City, State",
    "can_issue_documents": true,
    "can_request_documents": true
}
```

---

## 📄 Document Management

### List Document Categories
**Endpoint:** `GET /api/v1/documents/categories/`

**Description:** List all available document categories

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "count": 8,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Identity Documents",
            "description": "Government-issued identification documents",
            "icon": "id-card",
            "is_active": true,
            "created_at": "2025-07-20T00:00:00Z"
        },
        {
            "id": 2,
            "name": "Educational Documents",
            "description": "Academic certificates and transcripts",
            "icon": "graduation-cap",
            "is_active": true,
            "created_at": "2025-07-20T00:00:00Z"
        }
    ]
}
```

### List Documents
**Endpoint:** `GET /api/v1/documents/`

**Description:** List user's documents with filtering and search options

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `category`: Filter by category ID
- `trust_level`: Filter by trust level (user_uploaded, peer_shared, officially_issued)
- `status`: Filter by status (active, expired, revoked, archived)
- `search`: Search in title and description
- `ordering`: Sort by field (created_at, updated_at, title, file_size)
- `page`: Page number for pagination

**Response (200):**
```json
{
    "count": 15,
    "next": "http://api.example.com/api/v1/documents/?page=2",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Passport",
            "description": "Government-issued passport",
            "file": "https://api.example.com/media/documents/1/passport.pdf",
            "file_size": 2048576,
            "file_type": ".pdf",
            "original_filename": "passport.pdf",
            "owner": 1,
            "owner_email": "john@example.com",
            "owner_name": "John Doe",
            "category": 1,
            "category_name": "Identity Documents",
            "trust_level": "officially_issued",
            "issuer": 2,
            "issuer_name": "Government Agency",
            "issue_date": "2025-01-15T00:00:00Z",
            "status": "active",
            "tags": ["passport", "identity", "government"],
            "metadata": {
                "expiry_date": "2030-01-15",
                "country": "USA"
            },
            "is_encrypted": true,
            "expiry_date": "2030-01-15T00:00:00Z",
            "version": 1,
            "download_count": 5,
            "view_count": 12,
            "is_expired": false,
            "created_at": "2025-07-20T00:00:00Z",
            "updated_at": "2025-07-20T00:00:00Z"
        }
    ]
}
```

### Upload Document
**Endpoint:** `POST /api/v1/documents/`

**Description:** Upload new document with encryption and metadata

**Headers:** `Authorization: Bearer <access_token>`

**Request Body (multipart/form-data):**
```json
{
    "title": "Driver's License",
    "description": "State-issued driver's license",
    "file": "<file>",
    "category": 1,
    "trust_level": "officially_issued",
    "tags": ["license", "driving", "government"],
    "metadata": {
        "expiry_date": "2028-05-15",
        "state": "CA"
    },
    "expiry_date": "2028-05-15T00:00:00Z"
}
```

**Response (201):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Driver's License",
    "description": "State-issued driver's license",
    "file": "https://api.example.com/media/documents/1/drivers_license.pdf",
    "file_size": 1048576,
    "file_type": ".pdf",
    "original_filename": "drivers_license.pdf",
    "owner": 1,
    "owner_email": "john@example.com",
    "owner_name": "John Doe",
    "category": 1,
    "category_name": "Identity Documents",
    "trust_level": "officially_issued",
    "issuer": null,
    "issuer_name": null,
    "issue_date": null,
    "status": "active",
    "tags": ["license", "driving", "government"],
    "metadata": {
        "expiry_date": "2028-05-15",
        "state": "CA"
    },
    "is_encrypted": true,
    "expiry_date": "2028-05-15T00:00:00Z",
    "version": 1,
    "download_count": 0,
    "view_count": 0,
    "is_expired": false,
    "created_at": "2025-07-20T00:00:00Z",
    "updated_at": "2025-07-20T00:00:00Z"
}
```

### Get Document Details
**Endpoint:** `GET /api/v1/documents/{id}/`

**Description:** Retrieve detailed information about specific document

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Passport",
    "description": "Government-issued passport",
    "file": "https://api.example.com/media/documents/1/passport.pdf",
    "file_size": 2048576,
    "file_type": ".pdf",
    "original_filename": "passport.pdf",
    "owner": 1,
    "owner_email": "john@example.com",
    "owner_name": "John Doe",
    "category": 1,
    "category_name": "Identity Documents",
    "trust_level": "officially_issued",
    "issuer": 2,
    "issuer_name": "Government Agency",
    "issue_date": "2025-01-15T00:00:00Z",
    "status": "active",
    "tags": ["passport", "identity", "government"],
    "metadata": {
        "expiry_date": "2030-01-15",
        "country": "USA"
    },
    "is_encrypted": true,
    "expiry_date": "2030-01-15T00:00:00Z",
    "version": 1,
    "download_count": 5,
    "view_count": 12,
    "is_expired": false,
    "created_at": "2025-07-20T00:00:00Z",
    "updated_at": "2025-07-20T00:00:00Z"
}
```

### Update Document
**Endpoint:** `PUT /api/v1/documents/{id}/`

**Description:** Update document metadata and properties

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "title": "Updated Passport",
    "description": "Updated government-issued passport",
    "category": 1,
    "tags": ["passport", "identity", "government", "updated"],
    "metadata": {
        "expiry_date": "2030-01-15",
        "country": "USA",
        "updated": true
    },
    "expiry_date": "2030-01-15T00:00:00Z",
    "status": "active"
}
```

### Delete Document
**Endpoint:** `DELETE /api/v1/documents/{id}/`

**Description:** Permanently delete document from vault

**Headers:** `Authorization: Bearer <access_token>`

**Response (204):** No content

### Download Document
**Endpoint:** `POST /api/v1/documents/{id}/download/`

**Description:** Download document file

**Headers:** `Authorization: Bearer <access_token>`

**Response:** File download

### Document Statistics
**Endpoint:** `GET /api/v1/documents/stats/`

**Description:** Get document statistics and analytics

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "total_documents": 15,
    "total_size": 52428800,
    "documents_by_category": [
        {
            "category__name": "Identity Documents",
            "count": 5
        },
        {
            "category__name": "Educational Documents",
            "count": 3
        }
    ],
    "documents_by_trust_level": [
        {
            "trust_level": "officially_issued",
            "count": 8
        },
        {
            "trust_level": "user_uploaded",
            "count": 7
        }
    ],
    "recent_uploads": [...],
    "most_viewed": [...],
    "most_downloaded": [...]
}
```

### Bulk Actions
**Endpoint:** `POST /api/v1/documents/bulk_action/`

**Description:** Perform bulk actions on documents

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "document_ids": [
        "550e8400-e29b-41d4-a716-446655440000",
        "550e8400-e29b-41d4-a716-446655440001"
    ],
    "action": "delete"
}
```

**Response (200):**
```json
{
    "message": "Deleted 2 documents"
}
```

### Issue Document (Organization)
**Endpoint:** `POST /api/v1/documents/issue/`

**Description:** Organization-issued documents directly to user's vault

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "title": "Certificate of Completion",
    "description": "Course completion certificate",
    "file": "<file>",
    "category": 2,
    "target_user": 3,
    "tags": ["certificate", "education", "completion"],
    "metadata": {
        "course_name": "Advanced Python Programming",
        "completion_date": "2025-07-15"
    },
    "expiry_date": "2028-07-15T00:00:00Z"
}
```

---

## 🤝 Document Sharing & Requests

### List Document Shares
**Endpoint:** `GET /api/v1/sharing/requests/`

**Description:** List sent and received document share requests

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `status`: Filter by status (pending, accepted, declined, expired)
- `permission`: Filter by permission (view, download, edit, admin)
- `created_at`: Filter by creation date

**Response (200):**
```json
{
    "count": 8,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "document": "550e8400-e29b-41d4-a716-446655440000",
            "document_title": "Passport",
            "shared_by": 1,
            "shared_by_email": "john@example.com",
            "shared_by_name": "John Doe",
            "shared_with": 2,
            "shared_with_email": "jane@example.com",
            "shared_with_name": "Jane Smith",
            "permission": "view",
            "expires_at": "2025-08-20T00:00:00Z",
            "status": "pending",
            "message": "Please review my passport for verification",
            "created_at": "2025-07-20T00:00:00Z",
            "updated_at": "2025-07-20T00:00:00Z"
        }
    ]
}
```

### Create Document Share
**Endpoint:** `POST /api/v1/sharing/requests/`

**Description:** Create new document share request

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "document": "550e8400-e29b-41d4-a716-446655440000",
    "shared_with": 2,
    "permission": "view",
    "expires_at": "2025-08-20T00:00:00Z",
    "message": "Please review my passport for verification"
}
```

### Accept Document Share
**Endpoint:** `POST /api/v1/sharing/requests/{id}/accept/`

**Description:** Accept received document share

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "message": "Share accepted"
}
```

### Decline Document Share
**Endpoint:** `POST /api/v1/sharing/requests/{id}/decline/`

**Description:** Decline received document share

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "message": "Share declined"
}
```

### Create Document Request
**Endpoint:** `POST /api/v1/sharing/requests/`

**Description:** Create new document request to another user

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "requestee": 2,
    "title": "Driver's License",
    "description": "I need your driver's license for verification purposes",
    "category": 1
}
```

### Approve Document Request
**Endpoint:** `POST /api/v1/sharing/requests/{id}/approve/`

**Description:** Approve received document request

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "message": "Request approved"
}
```

### Decline Document Request
**Endpoint:** `POST /api/v1/sharing/requests/{id}/decline/`

**Description:** Decline received document request

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "message": "Request declined"
}
```

---

## 📱 QR Code Sharing

### List QR Code Shares
**Endpoint:** `GET /api/v1/sharing/qr-shares/`

**Description:** List created QR code shares

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "document": "550e8400-e29b-41d4-a716-446655440000",
            "document_title": "Passport",
            "created_by": 1,
            "created_by_email": "john@example.com",
            "created_by_name": "John Doe",
            "title": "Passport Verification",
            "description": "QR code for passport verification",
            "permission": "view",
            "expires_at": "2025-07-25T00:00:00Z",
            "max_views": 1,
            "current_views": 0,
            "qr_code_image": "https://api.example.com/media/qr_codes/qr_share_550e8400.png",
            "qr_code_url": "https://api.example.com/media/qr_codes/qr_share_550e8400.png",
            "status": "active",
            "is_expired": false,
            "is_view_limit_reached": false,
            "is_active": true,
            "created_at": "2025-07-20T00:00:00Z",
            "updated_at": "2025-07-20T00:00:00Z"
        }
    ]
}
```

### Create QR Code Share
**Endpoint:** `POST /api/v1/sharing/qr-shares/`

**Description:** Generate QR code for temporary document sharing

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "document": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Passport Verification",
    "description": "QR code for passport verification",
    "permission": "view",
    "expires_at": "2025-07-25T00:00:00Z",
    "max_views": 1
}
```

### Revoke QR Code
**Endpoint:** `POST /api/v1/sharing/qr-shares/{id}/revoke/`

**Description:** Revoke QR code share

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
    "message": "QR code revoked"
}
```

### Bulk Create QR Codes
**Endpoint:** `POST /api/v1/sharing/qr-shares/bulk_create/`

**Description:** Create multiple QR codes for documents

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "document_ids": [
        "550e8400-e29b-41d4-a716-446655440000",
        "550e8400-e29b-41d4-a716-446655440001"
    ],
    "title": "Document Verification",
    "description": "QR codes for document verification",
    "permission": "view",
    "expires_at": "2025-07-25T00:00:00Z",
    "max_views": 1
}
```

### Access Shared Document via QR
**Endpoint:** `POST /api/v1/sharing/access/`

**Description:** Access shared documents via session token (public endpoint)

**Request Body:**
```json
{
    "qr_share_id": "550e8400-e29b-41d4-a716-446655440002",
    "session_token": "abc123def456..."
}
```

**Response (200):**
```json
{
    "document_title": "Passport",
    "document_description": "Government-issued passport",
    "permission": "view",
    "expires_at": "2025-07-25T00:00:00Z",
    "created_by_name": "John Doe",
    "access_url": "https://api.example.com/api/v1/sharing/access/abc123def456/",
    "download_url": null
}
```

---

## 🔑 OAuth2 Token Management

### OAuth2 Authorization
**Endpoint:** `GET /o/authorize/`

**Description:** OAuth2 authorization endpoint

**Query Parameters:**
- `client_id`: OAuth client ID
- `response_type`: Response type (code)
- `scope`: Requested scopes (read, write, documents, sharing)
- `redirect_uri`: Redirect URI after authorization
- `state`: State parameter for security

**Response:** Redirect to authorization page

### OAuth2 Token
**Endpoint:** `POST /o/token/`

**Description:** Generate OAuth2 access tokens using authorization code

**Request Body:**
```json
{
    "grant_type": "authorization_code",
    "code": "authorization_code_here",
    "client_id": "client_id_here",
    "client_secret": "client_secret_here",
    "redirect_uri": "https://client.example.com/callback"
}
```

**Response (200):**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "scope": "read write documents sharing"
}
```

### Revoke OAuth2 Token
**Endpoint:** `POST /o/revoke_token/`

**Description:** Revoke existing access tokens

**Request Body:**
```json
{
    "token": "access_token_here",
    "client_id": "client_id_here",
    "client_secret": "client_secret_here"
}
```

**Response (200):**
```json
{
    "message": "Token revoked successfully"
}
```

---

## 📊 API Documentation

### OpenAPI Schema
**Endpoint:** `GET /api/schema/`

**Description:** OpenAPI schema definition

**Response:** OpenAPI 3.0 schema in JSON format

### Swagger UI
**Endpoint:** `GET /api/docs/`

**Description:** Interactive Swagger UI documentation

**Response:** Swagger UI interface

### ReDoc
**Endpoint:** `GET /api/redoc/`

**Description:** ReDoc API documentation interface

**Response:** ReDoc interface

---

## ⚠️ Error Handling

### Error Response Format
All error responses follow this format:

```json
{
    "error": "Error message",
    "detail": "Detailed error information",
    "code": "ERROR_CODE"
}
```

### Common Error Codes
- `400`: Bad Request - Invalid request data
- `401`: Unauthorized - Authentication required
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server error

### Example Error Responses

**400 Bad Request:**
```json
{
    "error": "Validation failed",
    "detail": {
        "email": ["This field is required."],
        "password": ["This password is too short."]
    },
    "code": "VALIDATION_ERROR"
}
```

**401 Unauthorized:**
```json
{
    "error": "Authentication credentials were not provided",
    "detail": "Please provide valid authentication credentials",
    "code": "AUTHENTICATION_REQUIRED"
}
```

**403 Forbidden:**
```json
{
    "error": "You do not have permission to perform this action",
    "detail": "This document belongs to another user",
    "code": "PERMISSION_DENIED"
}
```

**404 Not Found:**
```json
{
    "error": "Document not found",
    "detail": "The requested document does not exist",
    "code": "RESOURCE_NOT_FOUND"
}
```

---

## 🚦 Rate Limiting

### Rate Limits
- **Anonymous users:** 100 requests per hour
- **Authenticated users:** 1000 requests per hour
- **API endpoints:** 10 requests per minute per IP

### Rate Limit Headers
Response headers include rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response
```json
{
    "error": "Rate limit exceeded",
    "detail": "You have exceeded the rate limit. Please try again later.",
    "code": "RATE_LIMIT_EXCEEDED"
}
```

---

## 🔧 Authentication Scopes

### Available Scopes
- `read`: Read access to user data
- `write`: Write access to user data
- `documents`: Full document management access
- `sharing`: Document sharing and request features

### Scope Usage
Scopes are used in OAuth2 authorization and determine the level of access granted to third-party applications.

---

## 📝 Notes

1. **File Uploads**: All file uploads support multipart/form-data format
2. **Pagination**: List endpoints support pagination with `page` parameter
3. **Filtering**: Most list endpoints support filtering by various fields
4. **Search**: Document endpoints support full-text search
5. **Ordering**: List endpoints support ordering by specified fields
6. **Rate Limiting**: All endpoints are subject to rate limiting
7. **CORS**: API supports CORS for cross-origin requests
8. **SSL**: Production endpoints require HTTPS
9. **Versioning**: API versioning is handled via URL path (`/api/v1/`)
10. **Documentation**: Interactive documentation available at `/api/docs/`

---

## 🚀 Getting Started

1. **Register a user account** using the registration endpoint
2. **Authenticate** using the login endpoint to get access tokens
3. **Upload documents** using the document upload endpoint
4. **Share documents** using the sharing endpoints
5. **Generate QR codes** for temporary sharing
6. **Manage organization profiles** for document issuance
7. **Use OAuth2** for third-party integrations

For more information, visit the interactive API documentation at `/api/docs/`. 