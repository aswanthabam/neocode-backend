# Complete API Integration Guide for Flutter Client

## Base URL: https://6d271e879a3e.ngrok-free.app

---

## 🔐 AUTHENTICATION APIs

### 1. User Registration

**Endpoint:** `POST /api/v1/auth/register/`
**Description:** Create a new user account

```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "user_type": "individual",
  "auth_provider": "email"
}
```

**Response:**

```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "username": "johndoe",
    "vault_id": "vault_123",
    "user_type": "individual",
    "is_verified": false,
    "created_at": "2025-07-20T10:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### 2. User Login

**Endpoint:** `POST /api/v1/auth/login/`
**Description:** Authenticate user with email and password

```json
{
  "email": "john.doe@example.com",
  "password": "SecurePass123!"
}
```

**Response:** Same as registration response

### 3. Token Refresh

**Endpoint:** `POST /api/v1/auth/token/refresh/`
**Description:** Refresh access token using refresh token

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 4. Logout

**Endpoint:** `POST /api/v1/auth/logout/`
**Description:** Logout user and blacklist refresh token
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**

```json
{
  "message": "Logout successful"
}
```

### 5. Password Change

**Endpoint:** `POST /api/v1/auth/password/change/`
**Description:** Change user password
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "old_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "new_password_confirm": "NewSecurePass456!"
}
```

**Response:**

```json
{
  "message": "Password changed successfully"
}
```

---

## 👤 USER PROFILE APIs

### 6. Get User Profile

**Endpoint:** `GET /api/v1/auth/profile/`
**Description:** Retrieve current user's profile information
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
{
  "id": 1,
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "username": "johndoe",
  "vault_id": "vault_123",
  "user_type": "individual",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "address": "123 Main St, City, Country",
  "profile_picture": null,
  "is_verified": false,
  "notification_preferences": {
    "email_notifications": true,
    "push_notifications": true
  },
  "privacy_settings": {
    "profile_visibility": "private",
    "show_email": false
  },
  "created_at": "2025-07-20T10:00:00Z",
  "updated_at": "2025-07-20T10:00:00Z"
}
```

### 7. Update User Profile

**Endpoint:** `PUT /api/v1/auth/profile/`
**Description:** Update current user's profile details
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "full_name": "John Updated Doe",
  "username": "johnupdated",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-01",
  "address": "123 Main St, City, Country"
}
```

**Response:** Updated user profile object

---

## 🔒 SECURITY SETTINGS APIs

### 8. Get Security Settings

**Endpoint:** `GET /api/v1/auth/security/settings/`
**Description:** Retrieve user's security settings
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
{
  "secret_pin": null,
  "pin_created_at": null,
  "pin_last_used": null,
  "biometric_enabled": false,
  "biometric_type": null,
  "require_pin_for_downloads": false,
  "require_pin_for_sharing": false,
  "require_pin_for_deletion": false,
  "auto_lock_timeout": 300,
  "max_login_attempts": 5,
  "lockout_duration": 900,
  "two_factor_enabled": false,
  "backup_codes": [],
  "created_at": "2025-07-20T10:00:00Z",
  "updated_at": "2025-07-20T10:00:00Z"
}
```

### 9. Update Security Settings

**Endpoint:** `PUT /api/v1/auth/security/settings/`
**Description:** Update user's security settings
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "new_pin": "1234",
  "biometric_enabled": true,
  "biometric_type": "fingerprint",
  "require_pin_for_downloads": true,
  "require_pin_for_sharing": true,
  "require_pin_for_deletion": true,
  "auto_lock_timeout": 300,
  "max_login_attempts": 5,
  "lockout_duration": 900,
  "two_factor_enabled": false
}
```

**Response:** Updated security settings object

### 10. Verify PIN

**Endpoint:** `POST /api/v1/auth/security/verify-pin/`
**Description:** Verify user's secret PIN
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "pin": "1234"
}
```

**Response:**

```json
{
  "message": "PIN verified successfully",
  "verified": true
}
```

---

## 🏢 ORGANIZATION APIs

### 11. Get Organization Profile

**Endpoint:** `GET /api/v1/auth/organization/`
**Description:** Retrieve organization profile information
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
{
  "id": 1,
  "user": 1,
  "user_email": "john.doe@example.com",
  "user_full_name": "John Doe",
  "name": "Acme Corporation",
  "description": "A leading technology company",
  "organization_type": "corporation",
  "website": "https://acme.com",
  "email": "contact@acme.com",
  "phone": "+1234567890",
  "address": "456 Business Ave, Tech City",
  "is_verified": false,
  "verification_date": null,
  "can_issue_documents": true,
  "can_request_documents": true,
  "created_at": "2025-07-20T10:00:00Z",
  "updated_at": "2025-07-20T10:00:00Z"
}
```

### 12. Create Organization Profile

**Endpoint:** `POST /api/v1/auth/organization/`
**Description:** Create organization profile
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "name": "Acme Corporation",
  "description": "A leading technology company",
  "organization_type": "corporation",
  "website": "https://acme.com",
  "email": "contact@acme.com",
  "phone": "+1234567890",
  "address": "456 Business Ave, Tech City",
  "can_issue_documents": true,
  "can_request_documents": true
}
```

**Response:** Created organization object

### 13. Update Organization Profile

**Endpoint:** `PUT /api/v1/auth/organization/`
**Description:** Update organization profile details
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "name": "Acme Corporation Updated",
  "description": "Updated description",
  "website": "https://acme-updated.com"
}
```

**Response:** Updated organization object

---

## 📊 STATISTICS & ACTIVITY APIs

### 14. Get User Statistics

**Endpoint:** `GET /api/v1/auth/stats/`
**Description:** Get user statistics and activity summary
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
{
  "total_documents": 25,
  "shared_documents": 10,
  "received_documents": 5,
  "pending_requests": 3,
  "qr_shares_created": 8,
  "last_activity": "2025-07-20T10:00:00Z"
}
```

### 15. Get User Activities

**Endpoint:** `GET /api/v1/auth/activities/`
**Description:** Get list of user activities
**Headers:** `Authorization: Bearer <access_token>`
**Query Parameters:** `activity_type`, `created_at`
**Response:**

```json
[
  {
    "activity_type": "login",
    "description": "User logged in from 192.168.1.1",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "metadata": {},
    "created_at": "2025-07-20T10:00:00Z"
  }
]
```

### 16. Update Notification Preferences

**Endpoint:** `PUT /api/v1/auth/notifications/preferences/`
**Description:** Update user notification preferences
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "email_notifications": true,
  "push_notifications": false,
  "document_shared": true,
  "document_requested": true,
  "request_responded": true,
  "qr_accessed": true
}
```

**Response:** Updated notification preferences

### 17. Update Privacy Settings

**Endpoint:** `PUT /api/v1/auth/privacy/settings/`
**Description:** Update user privacy settings
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "profile_visibility": "private",
  "show_email": false,
  "show_phone": false,
  "allow_document_requests": true,
  "allow_qr_sharing": true
}
```

**Response:** Updated privacy settings

---

## 📄 DOCUMENT MANAGEMENT APIs

### 18. List Document Categories

**Endpoint:** `GET /api/v1/documents/categories/`
**Description:** Get list of all available document categories
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
[
  {
    "id": 1,
    "name": "Identity Documents",
    "description": "Government-issued identity documents",
    "icon": "id-card",
    "is_active": true,
    "created_at": "2025-07-20T10:00:00Z",
    "updated_at": "2025-07-20T10:00:00Z"
  }
]
```

### 19. Create Document Category

**Endpoint:** `POST /api/v1/documents/categories/`
**Description:** Create a new document category
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "name": "Financial Documents",
  "description": "Bank statements, tax returns, etc.",
  "icon": "bank"
}
```

**Response:** Created category object

### 20. List Documents

**Endpoint:** `GET /api/v1/documents/`
**Description:** Get list of user's documents
**Headers:** `Authorization: Bearer <access_token>`
**Query Parameters:** `category`, `trust_level`, `status`, `search`, `ordering`
**Response:**

```json
[
  {
    "id": 1,
    "title": "Passport",
    "description": "Government-issued passport",
    "original_filename": "passport.pdf",
    "encrypted_filename": "encrypted_passport.pdf",
    "file_type": "pdf",
    "file_size": 2048576,
    "trust_level": "high",
    "status": "active",
    "category": {
      "id": 1,
      "name": "Identity Documents"
    },
    "owner": {
      "id": 1,
      "full_name": "John Doe"
    },
    "tags": ["passport", "identity"],
    "metadata": {},
    "created_at": "2025-07-20T10:00:00Z",
    "updated_at": "2025-07-20T10:00:00Z"
  }
]
```

### 21. Upload Document

**Endpoint:** `POST /api/v1/documents/`
**Description:** Upload new document
**Headers:** `Authorization: Bearer <access_token>`, `Content-Type: multipart/form-data`

```json
{
  "title": "Passport",
  "description": "Government-issued passport",
  "file": "<file_data>",
  "category": 1,
  "trust_level": "high",
  "tags": ["passport", "identity"],
  "metadata": {}
}
```

**Response:** Created document object

### 22. Update Document

**Endpoint:** `PUT /api/v1/documents/{id}/`
**Description:** Update document metadata
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "title": "Updated Passport",
  "description": "Updated description",
  "category": 1,
  "trust_level": "critical",
  "tags": ["passport", "identity", "updated"]
}
```

**Response:** Updated document object

### 23. Delete Document

**Endpoint:** `DELETE /api/v1/documents/{id}/`
**Description:** Delete document permanently
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
{
  "message": "Document deleted successfully"
}
```

### 24. Download Document

**Endpoint:** `POST /api/v1/documents/{id}/download/`
**Description:** Download document file
**Headers:** `Authorization: Bearer <access_token>`
**Response:** Binary file response

### 25. Document Statistics

**Endpoint:** `GET /api/v1/documents/stats/`
**Description:** Get document statistics
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
{
  "total_documents": 25,
  "total_size": 52428800,
  "documents_by_category": {
    "Identity Documents": 10,
    "Financial Documents": 8,
    "Medical Records": 7
  },
  "documents_by_trust_level": {
    "low": 5,
    "medium": 10,
    "high": 8,
    "critical": 2
  },
  "documents_by_status": {
    "active": 20,
    "archived": 5
  },
  "recent_uploads": [
    {
      "id": 1,
      "title": "Passport",
      "created_at": "2025-07-20T10:00:00Z"
    }
  ]
}
```

---

## 🔗 DOCUMENT SHARING APIs

### 26. List Document Shares

**Endpoint:** `GET /api/v1/sharing/requests/`
**Description:** Get list of document shares
**Headers:** `Authorization: Bearer <access_token>`
**Query Parameters:** `status`, `permission`, `created_at`
**Response:**

```json
[
  {
    "id": 1,
    "document": {
      "id": 1,
      "title": "Passport"
    },
    "shared_by": {
      "id": 1,
      "full_name": "John Doe"
    },
    "shared_with": {
      "id": 2,
      "full_name": "Jane Smith"
    },
    "permission": "view",
    "status": "pending",
    "expires_at": "2025-08-20T10:00:00Z",
    "created_at": "2025-07-20T10:00:00Z",
    "updated_at": "2025-07-20T10:00:00Z"
  }
]
```

### 27. Share Document

**Endpoint:** `POST /api/v1/sharing/requests/`
**Description:** Share document with another user
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "document": 1,
  "user_email": "jane.smith@example.com",
  "permission": "view",
  "expires_at": "2025-08-20T10:00:00Z",
  "message": "Please review this document"
}
```

**Response:** Created share object

### 28. Accept/Decline Share

**Endpoint:** `POST /api/v1/sharing/requests/{id}/accept/`
**Endpoint:** `POST /api/v1/sharing/requests/{id}/decline/`
**Description:** Accept or decline document share
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
{
  "message": "Document share accepted"
}
```

---

## 📱 QR CODE SHARING APIs

### 29. List QR Code Shares

**Endpoint:** `GET /api/v1/sharing/qr-shares/`
**Description:** Get list of QR code shares
**Headers:** `Authorization: Bearer <access_token>`
**Query Parameters:** `status`, `permission`, `created_at`
**Response:**

```json
[
  {
    "id": 1,
    "document": {
      "id": 1,
      "title": "Passport"
    },
    "created_by": {
      "id": 1,
      "full_name": "John Doe"
    },
    "title": "Passport Access",
    "description": "Temporary access to passport",
    "permission": "view",
    "status": "active",
    "qr_code_url": "https://example.com/qr/abc123",
    "session_token": "session_abc123",
    "expires_at": "2025-07-21T10:00:00Z",
    "max_views": 10,
    "current_views": 3,
    "created_at": "2025-07-20T10:00:00Z",
    "updated_at": "2025-07-20T10:00:00Z"
  }
]
```

### 30. Create QR Code Share

**Endpoint:** `POST /api/v1/sharing/qr-shares/`
**Description:** Create QR code for temporary document sharing
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "document": 1,
  "title": "Passport Access",
  "description": "Temporary access to passport",
  "permission": "view",
  "expires_at": "2025-07-21T10:00:00Z",
  "max_views": 10
}
```

**Response:** Created QR code share object

### 31. Revoke QR Code

**Endpoint:** `POST /api/v1/sharing/qr-shares/{id}/revoke/`
**Description:** Revoke QR code share
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
{
  "message": "QR code revoked successfully"
}
```

### 32. Bulk Create QR Codes

**Endpoint:** `POST /api/v1/sharing/qr-shares/bulk_create/`
**Description:** Create multiple QR codes for documents
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "document_ids": [1, 2, 3],
  "title": "Bulk Access",
  "description": "Access to multiple documents",
  "permission": "view",
  "expires_at": "2025-07-21T10:00:00Z",
  "max_views": 5
}
```

**Response:**

```json
{
  "message": "Created 3 QR codes",
  "qr_shares": [...]
}
```

### 33. Access Document via QR Code

**Endpoint:** `POST /api/v1/sharing/access/`
**Description:** Access shared document via QR code (public endpoint)

```json
{
  "session_token": "session_abc123"
}
```

**Response:**

```json
{
  "document": {
    "id": 1,
    "title": "Passport",
    "description": "Government-issued passport"
  },
  "permission": "view",
  "expires_at": "2025-07-21T10:00:00Z",
  "remaining_views": 7,
  "access_token": "access_abc123"
}
```

---

## 📋 DOCUMENT REQUESTS APIs

### 34. List Document Requests

**Endpoint:** `GET /api/v1/sharing/requests/`
**Description:** Get list of document requests
**Headers:** `Authorization: Bearer <access_token>`
**Query Parameters:** `status`, `category`, `created_at`
**Response:**

```json
[
  {
    "id": 1,
    "requester": {
      "id": 2,
      "full_name": "Jane Smith"
    },
    "issuer": {
      "id": 1,
      "full_name": "John Doe"
    },
    "title": "Employment Verification",
    "description": "Need employment verification letter",
    "category": {
      "id": 2,
      "name": "Employment Documents"
    },
    "status": "pending",
    "due_date": "2025-07-25T10:00:00Z",
    "reason": "For loan application",
    "created_at": "2025-07-20T10:00:00Z",
    "updated_at": "2025-07-20T10:00:00Z"
  }
]
```

### 35. Create Document Request

**Endpoint:** `POST /api/v1/sharing/requests/`
**Description:** Create document request
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "title": "Employment Verification",
  "description": "Need employment verification letter",
  "category": 2,
  "issuer_email": "john.doe@example.com",
  "due_date": "2025-07-25T10:00:00Z",
  "reason": "For loan application"
}
```

**Response:** Created request object

### 36. Approve/Decline Document Request

**Endpoint:** `POST /api/v1/sharing/requests/{id}/approve/`
**Endpoint:** `POST /api/v1/sharing/requests/{id}/decline/`
**Description:** Approve or decline document request
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "reason": "Request approved"
}
```

**Response:**

```json
{
  "message": "Document request approved"
}
```

---

## 📊 SHARING STATISTICS APIs

### 37. Get Sharing Statistics

**Endpoint:** `GET /api/v1/sharing/stats/`
**Description:** Get sharing statistics and analytics
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
{
  "total_shares": 15,
  "active_shares": 10,
  "total_qr_codes": 8,
  "active_qr_codes": 6,
  "shares_by_permission": {
    "view": 8,
    "download": 5,
    "edit": 2
  },
  "qr_codes_by_status": {
    "active": 6,
    "expired": 2
  },
  "recent_shares": [
    {
      "id": 1,
      "document": "Passport",
      "shared_with": "Jane Smith",
      "created_at": "2025-07-20T10:00:00Z"
    }
  ],
  "recent_qr_accesses": [
    {
      "id": 1,
      "document": "Passport",
      "accessed_at": "2025-07-20T10:00:00Z"
    }
  ]
}
```

### 38. Bulk Share Documents

**Endpoint:** `POST /api/v1/sharing/bulk/`
**Description:** Share multiple documents with users
**Headers:** `Authorization: Bearer <access_token>`

```json
{
  "document_ids": [1, 2, 3],
  "user_emails": ["user1@example.com", "user2@example.com"],
  "permission": "view",
  "expires_at": "2025-08-20T10:00:00Z",
  "message": "Bulk share of documents"
}
```

**Response:**

```json
{
  "message": "Shared 3 documents with 2 users",
  "shares_created": 6
}
```

---

## 🔔 NOTIFICATION APIs

### 39. List Share Notifications

**Endpoint:** `GET /api/v1/sharing/notifications/`
**Description:** Get list of share notifications
**Headers:** `Authorization: Bearer <access_token>`
**Query Parameters:** `notification_type`, `is_read`, `created_at`
**Response:**

```json
[
  {
    "id": 1,
    "notification_type": "document_shared",
    "title": "Document Shared",
    "message": "John Doe shared 'Passport' with you",
    "is_read": false,
    "metadata": {
      "document_id": 1,
      "shared_by": "John Doe"
    },
    "created_at": "2025-07-20T10:00:00Z"
  }
]
```

### 40. Mark Notification as Read

**Endpoint:** `POST /api/v1/sharing/notifications/{id}/mark_read/`
**Description:** Mark specific notification as read
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
{
  "message": "Notification marked as read"
}
```

### 41. Mark All Notifications as Read

**Endpoint:** `POST /api/v1/sharing/notifications/mark_all_read/`
**Description:** Mark all notifications as read
**Headers:** `Authorization: Bearer <access_token>`
**Response:**

```json
{
  "message": "All notifications marked as read"
}
```

---

## 🔧 FLUTTER INTEGRATION TIPS

### HTTP Client Setup

```dart
class ApiClient {
  static const String baseUrl = 'https://6d271e879a3e.ngrok-free.app/api/v1';
  static String? accessToken;

  static Future<http.Response> get(String endpoint) async {
    final response = await http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json',
      },
    );
    return response;
  }

  static Future<http.Response> post(String endpoint, Map<String, dynamic> data) async {
    final response = await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: {
        'Authorization': 'Bearer $accessToken',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(data),
    );
    return response;
  }
}
```

### Token Management

```dart
class TokenManager {
  static Future<void> saveTokens(String access, String refresh) async {
    await SharedPreferences.getInstance().then((prefs) {
      prefs.setString('access_token', access);
      prefs.setString('refresh_token', refresh);
    });
  }

  static Future<String?> getAccessToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }
}
```

### Error Handling

```dart
class ApiException implements Exception {
  final String message;
  final int statusCode;

  ApiException(this.message, this.statusCode);
}

Future<T> handleApiResponse<T>(http.Response response, T Function(Map<String, dynamic>) fromJson) {
  if (response.statusCode >= 200 && response.statusCode < 300) {
    return fromJson(jsonDecode(response.body));
  } else {
    throw ApiException(response.body, response.statusCode);
  }
}
```

### File Upload Example

```dart
Future<void> uploadDocument(File file, String title, int categoryId) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('${ApiClient.baseUrl}/documents/'),
  );

  request.headers['Authorization'] = 'Bearer ${ApiClient.accessToken}';
  request.fields['title'] = title;
  request.fields['category'] = categoryId.toString();
  request.fields['trust_level'] = 'high';

  request.files.add(await http.MultipartFile.fromPath('file', file.path));

  final response = await request.send();
  final responseData = await response.stream.bytesToString();

  if (response.statusCode == 201) {
    print('Document uploaded successfully');
  } else {
    throw ApiException(responseData, response.statusCode);
  }
}
```

---

## 📝 NOTES

1. **Authentication:** All protected endpoints require `Authorization: Bearer <access_token>` header
2. **File Uploads:** Use `multipart/form-data` for file uploads
3. **Error Responses:** All errors return appropriate HTTP status codes with error messages
4. **Pagination:** List endpoints support pagination with `page` and `page_size` parameters
5. **Filtering:** Most list endpoints support filtering via query parameters
6. **Search:** Document endpoints support search via `search` parameter
7. **Ordering:** List endpoints support ordering via `ordering` parameter

This guide covers all 41 APIs available in your secure file management backend for Flutter integration.
