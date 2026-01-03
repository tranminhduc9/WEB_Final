# BACKEND DOCUMENTATION - HANOIVIVU API

**Version:** 1.0.0  
**Last Updated:** 2026-01-03  
**Author:** Hoang Van Phu (Backend Developer)  
**Project:** Hanoivivu - Travel Platform for Hanoi Tourism

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Database Architecture](#4-database-architecture)
5. [API Endpoints Reference](#5-api-endpoints-reference)
6. [Authentication and Authorization](#6-authentication-and-authorization)
7. [Middleware Components](#7-middleware-components)
8. [Services Layer](#8-services-layer)
9. [Configuration and Environment Variables](#9-configuration-and-environment-variables)
10. [File Upload System](#10-file-upload-system)
11. [AI Chatbot Integration](#11-ai-chatbot-integration)
12. [Security Considerations](#12-security-considerations)
13. [Monitoring and Logging](#13-monitoring-and-logging)
14. [Running the Backend Server](#14-running-the-backend-server)

---

## 1. System Overview

### 1.1 Description

Hanoivivu API is a RESTful backend service built with FastAPI framework, designed to power a travel platform focused on Hanoi tourism. The system provides comprehensive features including user management, place discovery, social posts/reviews, AI-powered travel assistant, and administrative tools.

### 1.2 Key Features

- **User Authentication**: JWT-based authentication with access/refresh token mechanism
- **Place Management**: CRUD operations for tourist destinations, restaurants, hotels
- **Social Features**: User posts/reviews, comments, likes, and reporting system
- **AI Chatbot**: Google Gemini AI integration for travel assistance
- **Admin Panel**: Comprehensive dashboard for content moderation and analytics
- **File Upload**: Support for local storage and AWS S3 integration
- **Email Services**: SendGrid integration for transactional emails
- **Rate Limiting**: Protection against API abuse with sliding window algorithm

### 1.3 Architecture Pattern

The backend follows a layered architecture pattern:

```
+------------------+
|   API Routes     |  (app/api/v1/*.py)
+------------------+
        |
+------------------+
|    Services      |  (app/services/*.py)
+------------------+
        |
+------------------+
|   Middleware     |  (middleware/*.py)
+------------------+
        |
+------------------+
|   Data Layer     |  (config/database.py, middleware/mongodb_client.py)
+------------------+
        |
+------------------+
| PostgreSQL/MongoDB|
+------------------+
```

---

## 2. Technology Stack

### 2.1 Core Framework

| Component | Technology | Version |
|-----------|------------|---------|
| Web Framework | FastAPI | >= 0.104.0 |
| ASGI Server | Uvicorn | >= 0.24.0 |
| Python | Python | 3.9+ |

### 2.2 Databases

| Database | Purpose | Driver |
|----------|---------|--------|
| PostgreSQL | Primary data (users, places, roles) | SQLAlchemy 2.0 + psycopg2-binary |
| MongoDB | Social data (posts, comments, likes) | Motor (async) + PyMongo |
| Redis | Rate limiting storage (optional) | redis-py |

### 2.3 External Services

| Service | Purpose | Configuration |
|---------|---------|---------------|
| Google Gemini AI | Chatbot intelligence | CHATBOT_API_KEY |
| SendGrid | Email delivery | SENDGRID_API_KEY |
| Hunter.io | Email validation | HUNTER_IO_API_KEY |
| AWS S3 | Cloud file storage | AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY |

### 2.4 Dependencies

Full list in `requirements.txt`:

```
# FastAPI & Web Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
starlette>=0.27.0

# Database - PostgreSQL
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9
asyncpg>=0.29.0

# Database - MongoDB
motor>=3.3.0
pymongo>=4.6.0

# Authentication & Security
pyjwt>=2.8.0
bcrypt>=4.1.0
python-multipart>=0.0.6

# HTTP Client
httpx>=0.25.0

# Environment & Configuration
python-dotenv>=1.0.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# AI Chatbot - Google Gemini
google-generativeai>=0.3.0

# Utilities
certifi>=2023.7.22
aiofiles>=23.2.1

# Security - Content Sanitization
bleach>=6.0.0

# Email
aiosmtplib>=3.0.0
```

---

## 3. Project Structure

```
src/backend/
├── run.py                      # Server entry point
├── requirements.txt            # Python dependencies
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application instance
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── users.py        # User management endpoints
│   │       ├── places.py       # Place management endpoints
│   │       ├── posts.py        # Post/review endpoints
│   │       ├── admin.py        # Admin panel endpoints
│   │       ├── chatbot.py      # AI chatbot endpoints
│   │       ├── upload.py       # File upload endpoints
│   │       └── logs.py         # System logs endpoints
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── config.py           # Chatbot configuration
│   │   ├── gemini_service.py   # Google Gemini integration
│   │   ├── place_context.py    # Place context for AI
│   │   └── prompts.py          # AI prompt templates
│   ├── services/
│   │   ├── auth_service.py     # Authentication business logic
│   │   ├── logging_service.py  # Activity logging
│   │   ├── post_stats_sync.py  # Post statistics synchronization
│   │   └── rating_sync.py      # Rating synchronization service
│   └── utils/
│       ├── __init__.py
│       ├── content_sanitizer.py # XSS protection
│       ├── email_validator.py   # Hunter.io integration
│       ├── image_helpers.py     # Image URL generation
│       ├── place_helpers.py     # Place utility functions
│       └── timezone_helper.py   # Timezone utilities
├── config/
│   ├── __init__.py
│   ├── database.py             # PostgreSQL models and connection
│   ├── image_config.py         # Image URL configuration
│   ├── load_env.py             # Environment loading
│   └── settings.py             # Application settings
└── middleware/
    ├── __init__.py
    ├── auth.py                 # JWT authentication
    ├── audit_log.py            # Audit logging
    ├── config.py               # Middleware configuration
    ├── cors.py                 # CORS handling
    ├── email_service.py        # Email delivery
    ├── error_handler.py        # Global error handling
    ├── file_upload.py          # File upload handling
    ├── log_search.py           # Log search utilities
    ├── mongodb_client.py       # MongoDB connection and operations
    ├── rate_limit.py           # Rate limiting
    ├── request_size_limit.py   # Request size limiting
    ├── response.py             # Response formatting
    ├── search_logging.py       # Search logging
    ├── secure_cookies.py       # Cookie security
    ├── setup.py                # Middleware setup
    ├── throttle.py             # Login throttling
    └── validator.py            # Input validation
```

---

## 4. Database Architecture

### 4.1 PostgreSQL Database Schema

#### 4.1.1 Core Tables

**Table: roles**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT | Role identifier |
| role_name | VARCHAR(50) | UNIQUE, NOT NULL | Role name (admin, moderator, user) |

Default roles:
- `id=1`: admin
- `id=2`: moderator
- `id=3`: user

**Table: users**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT | User identifier |
| full_name | VARCHAR(255) | NOT NULL | Full name |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| role_id | INTEGER | FK(roles.id), DEFAULT=3 | User role |
| bio | VARCHAR(500) | NULLABLE | User biography |
| avatar_url | VARCHAR(500) | NULLABLE | Avatar image path |
| email_verified | BOOLEAN | DEFAULT=FALSE | Email verification status |
| is_banned | BOOLEAN | DEFAULT=FALSE | Ban status |
| ban_reason | VARCHAR(500) | NULLABLE | Reason for ban |
| is_deleted | BOOLEAN | DEFAULT=FALSE | Soft delete flag |
| reputation_score | INTEGER | DEFAULT=0 | User reputation |
| last_login | DATETIME | NULLABLE | Last login timestamp |
| created_at | DATETIME | DEFAULT=NOW | Creation timestamp |
| updated_at | DATETIME | DEFAULT=NOW | Update timestamp |

**Table: districts**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT | District identifier |
| name | VARCHAR(100) | UNIQUE, NOT NULL | District name |

**Table: place_types**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT | Type identifier |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Type name |

Default place types:
- `id=1`: Restaurant
- `id=2`: Hotel
- `id=3`: Tourist Attraction

**Table: places**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT | Place identifier |
| name | VARCHAR(255) | NOT NULL | Place name |
| district_id | INTEGER | FK(districts.id) | District reference |
| place_type_id | INTEGER | FK(place_types.id) | Type reference |
| description | TEXT | NULLABLE | Description |
| address_detail | VARCHAR(500) | NULLABLE | Detailed address |
| latitude | FLOAT | NULLABLE | GPS latitude |
| longitude | FLOAT | NULLABLE | GPS longitude |
| open_hour | TIME | NULLABLE | Opening time |
| close_hour | TIME | NULLABLE | Closing time |
| price_min | DECIMAL(10,2) | DEFAULT=0 | Minimum price |
| price_max | DECIMAL(10,2) | DEFAULT=0 | Maximum price |
| rating_average | FLOAT | DEFAULT=0 | Average rating |
| rating_count | INTEGER | DEFAULT=0 | Number of ratings |
| favorites_count | INTEGER | DEFAULT=0 | Favorite count |
| view_count | INTEGER | DEFAULT=0 | View count |
| created_at | DATETIME | DEFAULT=NOW | Creation timestamp |
| updated_at | DATETIME | DEFAULT=NOW | Update timestamp |

#### 4.1.2 Extension Tables

**Table: restaurants** (extends places)
| Column | Type | Constraints |
|--------|------|-------------|
| place_id | INTEGER | PK, FK(places.id) CASCADE |
| cuisine_type | VARCHAR(100) | NULLABLE |
| avg_price_per_person | DECIMAL(10,2) | NULLABLE |

**Table: hotels** (extends places)
| Column | Type | Constraints |
|--------|------|-------------|
| place_id | INTEGER | PK, FK(places.id) CASCADE |
| star_rating | INTEGER | NULLABLE |
| price_per_night | DECIMAL(10,2) | NULLABLE |
| check_in_time | TIME | NULLABLE |
| check_out_time | TIME | NULLABLE |

**Table: tourist_attractions** (extends places)
| Column | Type | Constraints |
|--------|------|-------------|
| place_id | INTEGER | PK, FK(places.id) CASCADE |
| ticket_price | DECIMAL(10,2) | NULLABLE |
| is_ticket_required | BOOLEAN | DEFAULT=TRUE |

#### 4.1.3 Junction Tables

**Table: user_place_favorites**
| Column | Type | Constraints |
|--------|------|-------------|
| user_id | INTEGER | PK, FK(users.id) |
| place_id | INTEGER | PK, FK(places.id) |
| created_at | DATETIME | DEFAULT=NOW |

**Table: user_post_favorites**
| Column | Type | Constraints |
|--------|------|-------------|
| user_id | INTEGER | PK, FK(users.id) |
| post_id | VARCHAR(100) | PK (MongoDB ObjectId) |
| created_at | DATETIME | DEFAULT=NOW |

**Table: place_images**
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT |
| place_id | INTEGER | FK(places.id) |
| image_url | VARCHAR(500) | NOT NULL |
| is_main | BOOLEAN | DEFAULT=FALSE |
| created_at | DATETIME | DEFAULT=NOW |

#### 4.1.4 Logging Tables

**Table: token_refresh**
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT |
| user_id | INTEGER | FK(users.id) |
| token | VARCHAR(500) | UNIQUE, NOT NULL |
| expires_at | DATETIME | NOT NULL |
| revoked | BOOLEAN | DEFAULT=FALSE |
| created_at | DATETIME | DEFAULT=NOW |

**Table: activity_logs**
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT |
| user_id | INTEGER | FK(users.id) |
| action_type | VARCHAR(100) | NOT NULL |
| details | TEXT | NULLABLE |
| ip_address | VARCHAR(50) | NULLABLE |
| created_at | DATETIME | DEFAULT=NOW |

**Table: visit_logs**
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, AUTO_INCREMENT |
| user_id | INTEGER | FK(users.id) |
| place_id | INTEGER | FK(places.id) |
| post_id | VARCHAR(100) | NULLABLE |
| ip_address | VARCHAR(50) | NULLABLE |
| user_agent | TEXT | NULLABLE |
| visited_at | DATETIME | DEFAULT=NOW |

### 4.2 MongoDB Collections

#### 4.2.1 posts_mongo
```json
{
  "_id": "ObjectId",
  "author_id": "integer (FK to PostgreSQL users.id)",
  "title": "string",
  "content": "string (sanitized HTML)",
  "images": ["string (URLs)"],
  "tags": ["string"],
  "related_place_id": "integer | null",
  "rating": "float (0-5) | null",
  "status": "string (pending|published|rejected)",
  "reject_reason": "string | null",
  "likes_count": "integer",
  "comments_count": "integer",
  "views_count": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

Indexes:
- `author_id` (ASCENDING)
- `status` (ASCENDING)
- `created_at` (DESCENDING)
- `related_place_id` (ASCENDING)

#### 4.2.2 post_likes_mongo
```json
{
  "_id": "ObjectId",
  "post_id": "string (ObjectId reference)",
  "user_id": "integer",
  "created_at": "datetime"
}
```

Indexes:
- `[post_id, user_id]` (COMPOUND, UNIQUE)

#### 4.2.3 post_comments_mongo
```json
{
  "_id": "ObjectId",
  "post_id": "string (ObjectId reference)",
  "author_id": "integer",
  "content": "string (sanitized)",
  "images": ["string"],
  "parent_id": "string | null (for replies)",
  "created_at": "datetime"
}
```

Indexes:
- `post_id` (ASCENDING)
- `author_id` (ASCENDING)
- `parent_id` (ASCENDING)
- `created_at` (DESCENDING)

#### 4.2.4 reports_mongo
```json
{
  "_id": "ObjectId",
  "target_type": "string (post|comment)",
  "target_id": "string",
  "reporter_id": "integer",
  "reason": "string",
  "description": "string | null",
  "status": "string (pending|resolved|dismissed)",
  "resolved_by": "integer | null",
  "resolved_at": "datetime | null",
  "created_at": "datetime"
}
```

#### 4.2.5 chatbot_logs_mongo
```json
{
  "_id": "ObjectId",
  "conversation_id": "string (UUID)",
  "user_id": "integer",
  "user_message": "string",
  "bot_response": "string",
  "entities": "object (extracted entities)",
  "created_at": "datetime"
}
```

---

## 5. API Endpoints Reference

### 5.1 Authentication Endpoints

**Base Path:** `/api/v1/auth`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register new user | No |
| POST | `/login` | User login | No |
| POST | `/refresh` | Refresh access token | No |
| POST | `/logout` | User logout | Optional |
| GET | `/me` | Get current user info | Yes |
| GET | `/verify-email` | Verify email address | No |

**POST /register**
```json
// Request
{
  "full_name": "Nguyen Van A",
  "email": "user@example.com",
  "password": "password123"
}

// Response (201)
{
  "success": true,
  "message": "Registration successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "role_id": 3
  },
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer"
}
```

**POST /login**
```json
// Request
{
  "email": "user@example.com",
  "password": "password123"
}

// Response (200)
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "role_id": 3,
    "avatar_url": "https://..."
  },
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer"
}
```

### 5.2 User Endpoints

**Base Path:** `/api/v1/users`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/me` | Get current user profile | Yes |
| PUT | `/me` | Update current user profile | Yes |
| GET | `/profile` | Get profile (alias) | Yes |
| PUT | `/profile` | Update profile (alias) | Yes |
| PUT | `/change-password` | Change password | Yes |
| POST | `/avatar` | Upload avatar | Yes |
| DELETE | `/avatar` | Delete avatar | Yes |
| GET | `/{user_id}` | Get public user info | No |
| DELETE | `/favorites/{place_id}` | Remove favorite place | Yes |

### 5.3 Places Endpoints

**Base Path:** `/api/v1/places`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Get places list | No |
| GET | `/search` | Search places | No |
| GET | `/suggestions` | Search suggestions | No |
| GET | `/nearby` | Get nearby places | No |
| GET | `/districts` | Get all districts | No |
| GET | `/types` | Get place types | No |
| GET | `/{place_id}` | Get place detail | Optional |
| POST | `/{place_id}/favorite` | Toggle favorite | Yes |

**GET /search**

Query Parameters:
- `keyword`: Search keyword (optional)
- `district_id`: Filter by district (optional)
- `place_type_id`: Filter by type (optional)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 50)

### 5.4 Posts Endpoints

**Base Path:** `/api/v1/posts`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Get posts feed | Optional |
| POST | `/` | Create new post | Yes |
| GET | `/{post_id}` | Get post detail | Optional |
| DELETE | `/{post_id}` | Delete own post | Yes |
| POST | `/{post_id}/like` | Toggle like | Yes |
| POST | `/{post_id}/comment` | Add comment | Yes |
| POST | `/{post_id}/favorite` | Toggle favorite | Yes |
| POST | `/{post_id}/report` | Report post | Yes |
| POST | `/comments/{comment_id}/reply` | Reply to comment | Yes |
| POST | `/comments/{comment_id}/report` | Report comment | Yes |
| DELETE | `/comments/{comment_id}` | Delete comment | Yes |

**GET /** (Posts Feed)

Query Parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `sort`: Sort order - `newest` or `popular` (default: newest)

### 5.5 Admin Endpoints

**Base Path:** `/api/v1/admin`

All admin endpoints require authentication with `role_id = 1` (admin).

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Get dashboard statistics |
| GET | `/users` | Get users list |
| DELETE | `/users/{user_id}` | Delete user (soft) |
| PATCH | `/users/{user_id}/ban` | Ban user |
| PATCH | `/users/{user_id}/unban` | Unban user |
| GET | `/posts` | Get posts list |
| POST | `/posts` | Create post (auto-approved) |
| PUT | `/posts/{post_id}` | Update post |
| DELETE | `/posts/{post_id}` | Delete post |
| PATCH | `/posts/{post_id}/status` | Approve/reject post |
| GET | `/comments` | Get comments list |
| DELETE | `/comments/{comment_id}` | Delete comment |
| GET | `/reports` | Get reports list |
| POST | `/reports/{report_id}/resolve` | Resolve report |
| POST | `/reports/{report_id}/dismiss` | Dismiss report |
| GET | `/places` | Get places list |
| POST | `/places` | Create place |
| PUT | `/places/{place_id}` | Update place |
| DELETE | `/places/{place_id}` | Delete place |
| POST | `/places/{place_id}/images` | Upload place images |

### 5.6 Chatbot Endpoints

**Base Path:** `/api/v1/chatbot`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/message` | Send message to AI | Yes |
| GET | `/history` | Get chat history | Yes |
| GET | `/health` | Health check | No |

**POST /message**
```json
// Request
{
  "conversation_id": "optional-uuid",
  "message": "What are the best restaurants in Hoan Kiem?"
}

// Response
{
  "success": true,
  "conversation_id": "uuid",
  "bot_response": "Here are some great restaurants...",
  "suggested_places": [
    {
      "id": 1,
      "name": "Restaurant Name",
      "district_name": "Hoan Kiem",
      "rating_average": 4.5,
      "main_image_url": "https://..."
    }
  ]
}
```

### 5.7 Upload Endpoints

**Base Path:** `/api/v1/upload`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/` | Upload files | Yes |

**POST /**

Form Data:
- `files`: Multiple files (max 10 files)
- `folder`: Target folder - `places`, `avatars`, `posts`, `misc` (default: misc)
- `place_id`: Required for post uploads (naming convention)

### 5.8 Logs Endpoints

**Base Path:** `/api/v1/logs`

All logs endpoints require admin authentication.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/audit` | Get audit logs |
| GET | `/app` | Get application logs |
| GET | `/stats` | Get logging statistics |
| GET | `/visits` | Get visit logs |
| GET | `/analytics` | Get analytics summary |

---

## 6. Authentication and Authorization

### 6.1 JWT Token Structure

**Access Token Payload:**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "role_id": 3,
  "type": "access",
  "exp": 1704268800,
  "iat": 1704265200
}
```

**Refresh Token Payload:**
```json
{
  "user_id": 1,
  "type": "refresh",
  "exp": 1704870000,
  "iat": 1704265200
}
```

### 6.2 Token Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| JWT_SECRET_KEY | Required | Secret key for signing |
| JWT_ALGORITHM | HS256 | Signing algorithm |
| JWT_EXPIRATION | 3600 | Access token lifetime (seconds) |
| REFRESH_TOKEN_EXPIRATION | 604800 | Refresh token lifetime (7 days) |

### 6.3 Role-Based Access Control

| Role | role_id | Permissions |
|------|---------|-------------|
| admin | 1 | Full system access |
| moderator | 2 | Content moderation |
| user | 3 | Standard user access |

### 6.4 Authentication Flow

```
1. User registers or logs in
   Server validates credentials
   
2. Server generates tokens
   - Access Token (1 hour)
   - Refresh Token (7 days, stored in database)
   
3. Client stores tokens
   Sends access token in Authorization header
   
4. Token refresh
   - Access token expires
   - Client sends refresh token
   - Server issues new token pair
   
5. Logout
   Refresh token revoked in database
```

### 6.5 Password Security

- **Hashing Algorithm:** bcrypt
- **Rounds:** 12 (configurable via BCRYPT_ROUNDS)
- **Minimum Length:** 6 characters

---

## 7. Middleware Components

### 7.1 Rate Limiting

**File:** `middleware/rate_limit.py`

Implements sliding window rate limiting algorithm with configurable limits per endpoint.

**Rate Limit Tiers:**

| Tier | Requests/Minute | Applicable Endpoints |
|------|-----------------|---------------------|
| high | 5 | Login, Register, OTP |
| medium | 20 | Write actions (Post, Comment) |
| low | 60 | Read actions |
| admin | 30 | Admin endpoints |

**Configuration:**
```python
ENDPOINT_RATE_LIMITS = {
    "POST:/api/v1/auth/login": ("high", 60),
    "POST:/api/v1/auth/register": ("high", 60),
    "POST:/api/v1/posts": ("medium", 60),
    "GET:/api/v1/places": ("low", 60),
}
```

### 7.2 Login Throttling

**File:** `middleware/throttle.py`

Prevents brute-force attacks on login endpoints.

**Configuration:**
- `THROTTLE_MAX_ATTEMPTS`: 5 attempts
- `THROTTLE_LOCKOUT_DURATION`: 900 seconds (15 minutes)

### 7.3 CORS Configuration

**File:** `middleware/cors.py`

**Settings:**
```python
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
CORS_CREDENTIALS = True
CORS_MAX_AGE = 86400  # 24 hours
```

### 7.4 Request Size Limiting

**File:** `middleware/request_size_limit.py`

- `MAX_JSON_BODY_SIZE`: 1MB (1048576 bytes)
- `REQUEST_SIZE_LIMIT_ENABLED`: true/false

### 7.5 Content Sanitization

**File:** `app/utils/content_sanitizer.py`

- XSS attack detection and prevention
- HTML tag sanitization using bleach library
- Security event logging

### 7.6 Response Formatting

**File:** `middleware/response.py`

Standard response formats:

```python
# Success Response
{
    "success": true,
    "message": "Operation successful",
    "data": {...}
}

# Error Response
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description"
    }
}
```

---

## 8. Services Layer

### 8.1 Authentication Service

**File:** `app/services/auth_service.py`

Handles:
- User registration with email validation
- Login with password verification
- Token generation and refresh
- Session management

### 8.2 Rating Sync Service

**File:** `app/services/rating_sync.py`

Synchronizes ratings between MongoDB posts and PostgreSQL places.

**Functions:**
- `calculate_place_rating_from_mongodb()`: Calculate rating from approved posts
- `update_place_rating()`: Update single place rating
- `sync_all_place_ratings()`: Batch sync all places
- `on_post_approved()`: Handler for post approval
- `on_post_rejected_or_deleted()`: Handler for post removal

### 8.3 Logging Service

**File:** `app/services/logging_service.py`

Provides:
- Activity logging
- Visit tracking
- Search logging

### 8.4 Email Service

**File:** `middleware/email_service.py`

SendGrid integration for:
- Welcome emails
- Password reset emails
- Password change notifications

---

## 9. Configuration and Environment Variables

### 9.1 Environment File Structure

Location: `src/.env` (copy from `src/.env.example`)

### 9.2 Required Variables

```bash
# Application Environment
ENVIRONMENT=development|production
DEBUG=true|false

# PostgreSQL Database
DATABASE_URL=postgresql://user:password@host:port/database
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_password
POSTGRES_DB=travel_db
DB_PORT=5433

# MongoDB
MONGO_URI=mongodb://localhost:27017 or mongodb+srv://...
MONGO_DB_NAME=hanoivivu_mongo

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
REFRESH_TOKEN_EXPIRATION=604800

# Server
BACKEND_HOST=127.0.0.1  # Use 0.0.0.0 for production
BACKEND_PORT=8080
```

### 9.3 Optional Variables

```bash
# Database Pool Settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_SSL_MODE=prefer|require|verify-full

# Rate Limiting
RATE_LIMIT_ENABLED=true
THROTTLE_ENABLED=true
THROTTLE_MAX_ATTEMPTS=5
THROTTLE_LOCKOUT_DURATION=900

# Email - SendGrid
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=your_email@example.com
FROM_NAME=Hanoivivu

# Email Validation - Hunter.io
HUNTER_IO_API_KEY=your_hunter_io_api_key
HUNTER_IO_DEBUG=false

# File Upload
MAX_FILE_SIZE=5242880  # 5MB
UPLOADS_BASE_URL=http://127.0.0.1:8080/static/uploads

# AWS S3 (for production)
USE_S3=true|false
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_S3_BUCKET=your-bucket-name
AWS_S3_REGION=ap-southeast-2

# Chatbot - Google Gemini
CHATBOT_ENABLED=true
CHATBOT_API_KEY=your_gemini_api_key
CHATBOT_MODEL=gemini-1.5-flash
CHATBOT_TEMPERATURE=0.7
CHATBOT_MAX_TOKENS=2048
CHATBOT_TIMEOUT=30.0

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_CREDENTIALS=true
FRONTEND_URL=http://localhost:5173

# Cookies
COOKIE_SECURE=false  # Set true for HTTPS
COOKIE_SAME_SITE=lax
COOKIE_ACCESS_MAX_AGE=3600
COOKIE_REFRESH_MAX_AGE=604800

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Logging
ENABLE_AUDIT_LOG=true
ENABLE_SEARCH_LOGGING=true
```

---

## 10. File Upload System

### 10.1 Architecture

The system supports two storage modes:
- **Local Storage**: Development environment
- **AWS S3**: Production environment

### 10.2 Folder Structure

```
uploads/
├── places/       # Place images (place_{id}_{index}.{ext})
├── avatars/      # User avatars (avatar_{user_id}.{ext})
├── posts/        # Post images (post_{user_id}_{place_id}_{index}.{ext})
└── misc/         # Miscellaneous uploads
```

### 10.3 Image URL Configuration

**File:** `config/image_config.py`

```python
# Local URL format
http://127.0.0.1:8080/static/uploads/{folder}/{filename}

# S3 URL format
https://{bucket}.s3.{region}.amazonaws.com/static/uploads/{folder}/{filename}
```

### 10.4 Naming Conventions

| Image Type | Format |
|------------|--------|
| Place | `place_{place_id}_{index}.{ext}` |
| Avatar | `avatar_{user_id}.{ext}` |
| Post | `post_{user_id}_{place_id}_{index}.{ext}` |

### 10.5 Upload Limits

- Maximum file size: 10MB
- Allowed extensions: png, jpg, jpeg, gif, webp
- Maximum files per request: 10

---

## 11. AI Chatbot Integration

### 11.1 Architecture

The chatbot uses Google Gemini AI with place context injection for travel-related queries.

**Components:**
- `chatbot/gemini_service.py`: Gemini API integration
- `chatbot/place_context.py`: Place search and context building
- `chatbot/prompts.py`: System prompts and templates
- `chatbot/config.py`: Configuration settings

### 11.2 Conversation Flow

```
1. User sends message
   
2. System searches relevant places
   - Keyword extraction from message
   - Database query for matching places
   
3. Build AI context
   - Place information
   - Conversation history
   
4. Generate response via Gemini API
   
5. Save conversation to MongoDB
   
6. Return response with suggested places
```

### 11.3 Configuration

```bash
CHATBOT_API_KEY=your_gemini_api_key
CHATBOT_MODEL=gemini-1.5-flash
CHATBOT_TEMPERATURE=0.7
CHATBOT_MAX_TOKENS=2048
CHATBOT_TIMEOUT=30.0
```

---

## 12. Security Considerations

### 12.1 Authentication Security

- Passwords hashed with bcrypt (12 rounds)
- JWT tokens with configurable expiration
- Refresh tokens stored in database with revocation support
- Login throttling to prevent brute-force attacks

### 12.2 Input Validation

- Pydantic models for request validation
- Content sanitization against XSS attacks
- SQL injection prevention via SQLAlchemy ORM
- NoSQL injection prevention in MongoDB queries

### 12.3 Rate Limiting

- Per-endpoint rate limits
- IP-based and user-based identification
- Sliding window algorithm for accuracy

### 12.4 CORS Configuration

- Whitelist-based origin validation
- Credentials support with secure configuration
- Preflight request caching

### 12.5 SSL/TLS

- Database SSL configuration for production
- HTTPS enforcement for cookies
- HSTS headers support

### 12.6 Best Practices

1. Always use environment variables for secrets
2. Enable rate limiting in production
3. Use HTTPS with COOKIE_SECURE=true
4. Configure proper CORS origins
5. Enable audit logging
6. Regular security updates for dependencies

---

## 13. Monitoring and Logging

### 13.1 Logging Levels

| Level | Usage |
|-------|-------|
| DEBUG | Detailed debugging information |
| INFO | General operational information |
| WARNING | Warning messages |
| ERROR | Error events |

### 13.2 Log Locations

- **Application Logs**: Standard output (stdout)
- **Audit Logs**: PostgreSQL `activity_logs` table
- **Visit Logs**: PostgreSQL `visit_logs` table
- **Search Logs**: Configurable logging

### 13.3 Health Check

**Endpoint:** `GET /health`

```json
{
  "status": "healthy",
  "app": "Hanoivivu API",
  "version": "1.0.0",
  "database": "connected",
  "mongodb": "connected"
}
```

### 13.4 Admin Analytics

**Endpoint:** `GET /api/v1/logs/analytics`

Provides:
- User registration trends
- Page view statistics
- Post creation metrics
- Top viewed places/posts

---

## 14. Running the Backend Server

### 14.1 Development Mode

```bash
cd src/backend
python run.py
```

Options:
- `--reload`: Enable hot reload for development
- `--port 8000`: Custom port
- `--log-level debug`: Set log level

### 14.2 Production Mode

```bash
python run.py --prod
```

This will:
- Bind to `0.0.0.0` (accessible from all interfaces)
- Disable hot reload
- Use production settings from environment

### 14.3 Server URLs

| Environment | URL |
|-------------|-----|
| Development | http://127.0.0.1:8080 |
| Production | http://0.0.0.0:8080 |
| Swagger UI | http://{host}:8080/docs |
| ReDoc | http://{host}:8080/redoc |

---

## Appendix A: Error Codes

| Code | Description |
|------|-------------|
| INVALID_CREDENTIALS | Email or password incorrect |
| INVALID_TOKEN | JWT token invalid or expired |
| USER_NOT_FOUND | User does not exist |
| USER_BANNED | User account is banned |
| EMAIL_EXISTS | Email already registered |
| INVALID_EMAIL | Email validation failed |
| RATE_LIMIT_EXCEEDED | Too many requests |
| FORBIDDEN | Access denied |
| NOT_FOUND | Resource not found |
| INTERNAL_ERROR | Server error |

---

## Appendix B: API Response Examples

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total_pages": 5,
      "total_items": 50
    }
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email or password is incorrect"
  }
}
```

---

## Appendix C: Contact Information

**Backend Developer:** Hoang Van Phu  
**Project:** Hanoivivu - Travel Platform  
**Repository:** WEB_Final

---

*Document generated: 2026-01-03*  
*Version: 1.0.0*
