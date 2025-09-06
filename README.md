# Clinic Auth API

A production-ready FastAPI authentication service for clinic management systems, built with SQLite and SQLAlchemy 2.0 async.

## Features

- **JWT Authentication**: Access tokens (15m) and rotating refresh tokens (7d)
- **Password Security**: bcrypt hashing with secure password requirements
- **Email Integration**: Password reset via email (console logging in dev, SMTP in prod)
- **Rate Limiting**: Global and auth-specific rate limits with SlowAPI
- **Security Headers**: Comprehensive security middleware
- **Database**: SQLite with SQLAlchemy 2.0 async (aiosqlite)
- **Validation**: Pydantic v2 for request/response validation
- **Error Handling**: Structured error responses with proper HTTP codes
- **CORS**: Configurable cross-origin resource sharing

## Tech Stack

- **Framework**: FastAPI 0.115+
- **Database**: SQLite with aiosqlite driver
- **ORM**: SQLAlchemy 2.0 async
- **Authentication**: JWT with PyJWT
- **Password Hashing**: passlib with bcrypt
- **Email**: fastapi-mail
- **Rate Limiting**: SlowAPI
- **Validation**: Pydantic v2
- **Logging**: Loguru
- **Code Quality**: Black, Ruff, isort, mypy

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd clinic-auth-api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
APP_NAME=clinic-auth-api
APP_URL=http://localhost:8000
PORT=8000
DATABASE_URL=sqlite+aiosqlite:///./data/clinic_auth.db
JWT_ACCESS_SECRET=your_super_secret_access_key
JWT_REFRESH_SECRET=your_super_secret_refresh_key
JWT_ACCESS_EXPIRES=15m
JWT_REFRESH_EXPIRES=7d
RESET_TOKEN_EXPIRES_MIN=30
CORS_ORIGINS=http://localhost:3000
MAIL_FROM="Clinic Auth <no-reply@example.com>"
MAIL_SERVER=smtp.ethereal.email
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_TLS=True
```

### 3. Run the Application

```bash
# Development server
make dev
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
make run
# or
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Test the API

Visit the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Or use the provided test requests in `tests/requests.http`.

## API Endpoints

### Authentication

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| POST | `/api/auth/register` | Register new user | Global |
| POST | `/api/auth/login` | Login user | Auth (10/min) |
| POST | `/api/auth/refresh` | Refresh access token | Global |
| POST | `/api/auth/logout` | Logout user | Global |
| GET | `/api/auth/me` | Get current user | Global |
| POST | `/api/auth/forgot-password` | Send reset email | Auth (10/min) |
| POST | `/api/auth/reset-password` | Reset password | Global |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/HEAD | `/health` | Service health status |

## Database Schema

### Users Table
- `id`: UUID4 primary key
- `email`: Unique email address (lowercase)
- `password_hash`: bcrypt hashed password
- `name`: User's full name
- `role`: 'doctor' or 'admin' (default: 'doctor')
- `verified`: Email verification status
- `created_at`, `updated_at`: Timestamps

### Refresh Tokens Table
- `id`: UUID4 primary key
- `user_id`: Foreign key to users
- `jti`: Unique JWT ID
- `token_hash`: SHA256 hash of refresh token
- `user_agent`, `ip`: Client information
- `revoked`: Token revocation status
- `expires_at`: Token expiration
- `created_at`: Creation timestamp

### Reset Tokens Table
- `id`: UUID4 primary key
- `user_id`: Foreign key to users
- `token_hash`: SHA256 hash of reset token
- `expires_at`: Token expiration
- `created_at`: Creation timestamp

## Security Features

### JWT Tokens
- **Access Token**: 15 minutes, contains user ID and role
- **Refresh Token**: 7 days, contains user ID and JTI
- **Rotation**: New refresh token issued on each refresh
- **Revocation**: Tokens can be revoked and are checked against database

### Password Security
- Minimum 8 characters
- bcrypt hashing with salt
- Secure password requirements (letters, numbers, symbols)

### Rate Limiting
- **Global**: 100 requests per 15 minutes per IP
- **Auth endpoints**: 10 requests per minute per IP
- Headers include rate limit information

### Security Headers
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: geolocation=(), microphone=(), camera=()

## Development

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Clean up
make clean
```

### Testing

Use the provided HTTP requests file or test with curl:

```bash
# Register a user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Dr. Jane","email":"jane@example.com","password":"Str0ng!Pass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"jane@example.com","password":"Str0ng!Pass123"}'
```

## Production Deployment

### Environment Variables
Ensure all required environment variables are set, especially:
- Strong JWT secrets
- Proper CORS origins
- SMTP configuration for email

### Database
The SQLite database will be created automatically in the `data/` directory. For production, consider:
- Regular backups
- Database optimization
- Connection pooling

### Security
- Use HTTPS in production
- Set strong JWT secrets
- Configure proper CORS origins
- Enable SMTP for email notifications
- Monitor rate limiting

## Project Structure

```
clinic-auth-api/
├── app/
│   ├── models/          # SQLAlchemy ORM models
│   ├── repositories/    # Database CRUD operations
│   ├── schemas/         # Pydantic request/response models
│   ├── services/        # Business logic
│   ├── routes/          # API endpoints
│   ├── middleware/      # Custom middleware
│   ├── utils/           # Utility functions
│   ├── config.py        # Application configuration
│   ├── db.py           # Database connection
│   ├── deps.py         # FastAPI dependencies
│   └── main.py         # FastAPI application
├── tests/
│   └── requests.http   # API test requests
├── data/               # SQLite database directory
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── Makefile           # Development commands
└── README.md          # This file
```

## License

This project is licensed under the MIT License.
