# Clinic Auth API

A production-ready FastAPI authentication API with JWT tokens, MongoDB, and comprehensive security features.

## 🚀 Features

- **FastAPI** with async/await support
- **JWT Authentication** with access (15m) and refresh (7d) tokens
- **Token Rotation** and revocation
- **Password Reset** with email notifications
- **MongoDB** with Motor async driver
- **Rate Limiting** with SlowAPI
- **Security Headers** and CORS protection
- **Structured Logging** with Loguru
- **Input Validation** with Pydantic v2
- **Docker Compose** for development
- **Comprehensive Error Handling**

## 📋 Requirements

- Python 3.11+
- MongoDB 7.0+
- Docker & Docker Compose (for development)

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd clinic-auth-api
cp env.example .env
```

### 2. Configure Environment

Edit `.env` file with your settings:

```env
APP_NAME=clinic-auth-api
APP_URL=http://localhost:8000
PORT=8000
MONGO_URI=mongodb://localhost:27017/clinic_auth
JWT_ACCESS_SECRET=your-super-secret-access-key
JWT_REFRESH_SECRET=your-super-secret-refresh-key
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

### 3. Start Database

```bash
# Using Makefile
make db-up

# Or manually
docker-compose up -d mongodb mongo-express
```

### 4. Install Dependencies

```bash
# Using Makefile
make install

# Or manually
pip install -r requirements.txt
```

### 5. Start Development Server

```bash
# Using Makefile
make dev

# Or manually
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Test the API

The API will be available at `http://localhost:8000`

- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Mongo Express**: `http://localhost:8081` (admin/admin)

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login user | No |
| POST | `/api/auth/refresh` | Refresh access token | No |
| POST | `/api/auth/logout` | Logout user | No |
| GET | `/api/auth/me` | Get current user | Yes |
| POST | `/api/auth/forgot-password` | Request password reset | No |
| POST | `/api/auth/reset-password` | Reset password | No |

### System

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | No |
| HEAD | `/health` | Health check (HEAD) | No |

## 🧪 Testing

Use the provided `tests/requests.http` file with VS Code REST Client extension:

```http
### Register
POST http://localhost:8000/api/auth/register
Content-Type: application/json

{
  "name": "Dr Jane Smith",
  "email": "jane@example.com",
  "password": "Str0ng!Pass123"
}
```

## 🏗️ Project Structure

```
clinic-auth-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings
│   ├── db.py                   # Database connection
│   ├── deps.py                 # Dependencies
│   ├── models/                 # Data models
│   │   ├── user.py
│   │   └── token.py
│   ├── repositories/           # Database operations
│   │   ├── user_repo.py
│   │   ├── token_repo.py
│   │   └── reset_repo.py
│   ├── schemas/                # Request/Response schemas
│   │   ├── auth.py
│   │   └── user.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── jwt_service.py
│   │   ├── email_service.py
│   │   └── crypto_service.py
│   ├── routes/                 # API routes
│   │   └── auth_routes.py
│   ├── middleware/             # Custom middleware
│   │   ├── errors.py
│   │   └── security_headers.py
│   └── utils/                  # Utilities
│       └── responses.py
├── tests/
│   └── requests.http           # API test examples
├── docker-compose.yml          # Database services
├── mongo-init.js              # MongoDB initialization
├── requirements.txt           # Dependencies
├── pyproject.toml            # Project configuration
├── Makefile                  # Development commands
├── env.example               # Environment template
└── README.md                 # This file
```

## 🔧 Development Commands

```bash
# Install dependencies
make install

# Start development server
make dev

# Start database services
make db-up

# Stop all services
make stop

# Clean up containers
make clean

# Run linting
make lint

# Format code
make format

# Run all checks
make check
```

## 🔒 Security Features

- **JWT Tokens**: Access (15m) and refresh (7d) tokens
- **Token Rotation**: New refresh token on each refresh
- **Token Revocation**: Logout and password reset revoke tokens
- **Password Hashing**: bcrypt with salt
- **Rate Limiting**: Global and auth-specific limits
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, etc.
- **CORS Protection**: Configurable origins
- **Input Validation**: Pydantic v2 with comprehensive validation
- **Error Handling**: Consistent error responses

## 📊 Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "email": "string (unique, lowercase)",
  "password_hash": "string (bcrypt)",
  "name": "string",
  "role": "doctor|admin",
  "verified": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Refresh Tokens Collection
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "jti": "string (JWT ID)",
  "token_hash": "string (SHA256)",
  "user_agent": "string (optional)",
  "ip_address": "string (optional)",
  "revoked": "boolean",
  "expires_at": "datetime (TTL index)",
  "created_at": "datetime"
}
```

### Reset Tokens Collection
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "token_hash": "string (SHA256)",
  "expires_at": "datetime (TTL index)",
  "created_at": "datetime"
}
```

## 🚀 Production Deployment

1. **Environment Variables**: Set all required environment variables
2. **Database**: Use MongoDB Atlas or self-hosted MongoDB
3. **Email**: Configure SMTP settings for production
4. **Security**: Use strong JWT secrets and HTTPS
5. **Monitoring**: Add logging and monitoring
6. **Scaling**: Use multiple workers with Gunicorn

```bash
# Production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📞 Support

For support, email support@clinic.com or create an issue in the repository.