# Identity Service (identity-svc)

OAuth 2.1 / OpenID Connect Provider

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create `.env` file:**
```bash
cp .env.example .env
```

3. **Run the service:**
```bash
python -m uvicorn main:app --reload --port 8000
```

### Docker

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

## 📚 API Documentation

Once running, access:
- **Interactive API docs:** http://localhost:8000/docs
- **OpenID Configuration:** http://localhost:8000/.well-known/openid-configuration
- **JWKS endpoint:** http://localhost:8000/.well-known/jwks.json

## 🔑 Default Users

The service creates test users on startup:

| Username | Password | Roles |
|----------|----------|-------|
| `admin` | `admin123` | admin, user |
| `testuser` | `test123` | user |

## 🔐 OAuth 2.1 Flows

### Password Grant (Login)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=test123&grant_type=password"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

### Refresh Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

### Token Introspection

```bash
curl -X POST "http://localhost:8000/api/v1/auth/introspect?token=YOUR_TOKEN"
```

### Get User Info

```bash
curl -X GET "http://localhost:8000/api/v1/auth/userinfo" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 👤 User Management

### Register New User

```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "password123"
  }'
```

### Get Current User

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### List All Users (Admin only)

```bash
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

## 🏗️ Architecture

```
identity-svc/
├── domain/              # Business entities and rules
│   ├── entities/        # User, roles
│   └── repositories/    # Repository interfaces
├── application/         # Use cases and business logic
│   └── auth_service.py  # Authentication service
├── infraestructure/     # Technical implementations
│   ├── config/          # Settings and configuration
│   ├── crypto/          # RSA key management
│   └── repositories/    # Repository implementations
└── interfaces/          # API layer
    └── api/
        ├── v1/          # API version 1
        │   ├── schemas/ # Pydantic models
        │   ├── auth.py  # Auth endpoints
        │   ├── users.py # User endpoints
        │   └── discovery.py # OpenID endpoints
        ├── container.py # DI Container
        └── dependencies.py # FastAPI dependencies
└── main.py              # Application entry point
```

## 🔧 Configuration

Edit `.env` file:

```env
SERVICE_NAME=identity-svc
SERVICE_PORT=8000
JWT_ALGORITHM=RS256
JWT_EXPIRATION_MINUTES=30
REFRESH_TOKEN_EXPIRATION_DAYS=7
RSA_KEY_SIZE=2048
```

## 🧪 Testing

```bash
# Run tests (when implemented)
pytest

# Coverage
pytest --cov=.
```

## 📝 JWT Token Structure

Access Token payload:
```json
{
  "sub": "user-uuid",
  "username": "testuser",
  "email": "test@example.com",
  "roles": ["user"],
  "scopes": ["read", "write"],
  "type": "access_token",
  "exp": 1234567890,
  "iat": 1234567890
}
```

## 🔒 Security Features

- ✅ RS256 JWT signing (asymmetric)
- ✅ Password hashing with bcrypt
- ✅ Token expiration and refresh
- ✅ Role-based access control
- ✅ CORS configuration
- ✅ OpenID Connect Discovery

## 📦 Dependencies

- **FastAPI** - Modern web framework
- **python-jose** - JWT implementation
- **passlib** - Password hashing
- **cryptography** - RSA key generation
- **pydantic** - Data validation
- **SQLAlchemy** - ORM for database
- **aiosqlite** - Async SQLite driver

## 🗄️ Database

The service uses SQLite for persistence. The database file `identity.db` is created automatically on startup.

**Note:** For production, consider using PostgreSQL and implementing Alembic migrations.

## 🚀 Next Steps

1. Implement Alembic migrations
2. Implement authorization code flow
3. Add client credentials management
4. Migrate to PostgreSQL for production
5. Implement rate limiting
6. Add audit logging
7. Add email verification
8. Implement 2FA/MFA
