"""
API layer - FastAPI application for Identity Service
OAuth 2.1 / OpenID Connect Provider
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import logging
import sys
from pathlib import Path

# Add parent directory to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from application.auth_service import AuthenticationService, AuthenticationError, RegistrationError
from infraestructure.config.settings import get_settings
from infraestructure.crypto.rsa_manager import RSAKeyManager
from infraestructure.repositories.in_memory_user_repository import InMemoryUserRepository
from domain.entities.user import UserRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

# Initialize RSA key manager
rsa_manager = RSAKeyManager(keys_dir=settings.keys_directory)
rsa_manager.ensure_keys_exist()

# Initialize repository
user_repository = InMemoryUserRepository()

# Initialize authentication service
auth_service = AuthenticationService(
    user_repository=user_repository,
    private_key=rsa_manager.load_private_key(),
    public_key=rsa_manager.load_public_key(),
    algorithm=settings.jwt_algorithm,
    access_token_expire_minutes=settings.jwt_expiration_minutes,
    refresh_token_expire_days=settings.refresh_token_expiration_days
)

# Create FastAPI app
app = FastAPI(
    title="Identity Service",
    description="OAuth 2.1 / OpenID Connect Provider",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth/token")


# ==================== Pydantic Models ====================

class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    roles: List[str]
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenIntrospectionResponse(BaseModel):
    active: bool
    sub: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    roles: Optional[List[str]] = None
    exp: Optional[int] = None
    iat: Optional[int] = None


# ==================== Dependencies ====================

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get current user from token"""
    try:
        payload = await auth_service.verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==================== OpenID Connect Discovery ====================

@app.get("/.well-known/openid-configuration")
async def openid_configuration():
    """OpenID Connect Discovery endpoint"""
    return {
        "issuer": settings.issuer,
        "authorization_endpoint": f"{settings.issuer}/oauth/authorize",
        "token_endpoint": f"{settings.issuer}/oauth/token",
        "userinfo_endpoint": f"{settings.issuer}/oauth/userinfo",
        "jwks_uri": f"{settings.issuer}/.well-known/jwks.json",
        "introspection_endpoint": f"{settings.issuer}/oauth/introspect",
        "response_types_supported": ["code", "token"],
        "grant_types_supported": ["authorization_code", "password", "refresh_token"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "profile", "email"],
        "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"],
        "claims_supported": ["sub", "iss", "aud", "exp", "iat", "username", "email", "roles"]
    }


@app.get("/.well-known/jwks.json")
async def jwks():
    """JSON Web Key Set endpoint"""
    return rsa_manager.get_jwks()


# ==================== OAuth 2.1 Endpoints ====================

@app.post("/oauth/token", response_model=TokenResponse)
async def oauth_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth 2.1 Token endpoint
    Supports password grant type
    """
    try:
        tokens = await auth_service.login(
            username=form_data.username,
            password=form_data.password
        )
        logger.info(f"User {form_data.username} authenticated successfully")
        return tokens
    except AuthenticationError as e:
        logger.warning(f"Authentication failed for user {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/oauth/refresh", response_model=TokenResponse)
async def oauth_refresh(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        access_token = await auth_service.refresh_access_token(request.refresh_token)
        return {
            "access_token": access_token,
            "refresh_token": request.refresh_token,  # Keep same refresh token
            "token_type": "Bearer",
            "expires_in": settings.jwt_expiration_minutes * 60
        }
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/oauth/introspect", response_model=TokenIntrospectionResponse)
async def oauth_introspect(token: str):
    """Token introspection endpoint"""
    try:
        payload = await auth_service.verify_token(token)
        return TokenIntrospectionResponse(
            active=True,
            sub=payload.get("sub"),
            username=payload.get("username"),
            email=payload.get("email"),
            roles=payload.get("roles"),
            exp=payload.get("exp"),
            iat=payload.get("iat")
        )
    except AuthenticationError:
        return TokenIntrospectionResponse(active=False)


@app.get("/oauth/userinfo", response_model=UserResponse)
async def oauth_userinfo(current_user = Depends(get_current_user)):
    """OAuth UserInfo endpoint"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        roles=[role.value for role in current_user.roles],
        is_active=current_user.is_active
    )


# ==================== User Management Endpoints ====================

@app.post("/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegisterRequest):
    """Register a new user"""
    try:
        user = await auth_service.register_user(
            username=request.username,
            email=request.email,
            password=request.password
        )
        logger.info(f"New user registered: {user.username}")
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            roles=[role.value for role in user.roles],
            is_active=user.is_active
        )
    except RegistrationError as e:
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current authenticated user info"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        roles=[role.value for role in current_user.roles],
        is_active=current_user.is_active
    )


@app.get("/users", response_model=List[UserResponse])
async def list_users(current_user = Depends(get_current_user)):
    """List all users (admin only)"""
    # Check if user is admin
    if UserRole.ADMIN not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = await user_repository.list_all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            roles=[role.value for role in user.roles],
            is_active=user.is_active
        )
        for user in users
    ]


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "docs": "/docs",
        "openid_configuration": "/.well-known/openid-configuration"
    }


# ==================== Startup Event ====================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"🚀 Starting {settings.service_name} on port {settings.service_port}")
    logger.info(f"📝 OpenID Configuration: {settings.issuer}/.well-known/openid-configuration")
    logger.info(f"🔑 JWKS endpoint: {settings.issuer}/.well-known/jwks.json")
    
    # Create a default admin user for testing
    try:
        admin_user = await auth_service.register_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            roles=[UserRole.ADMIN, UserRole.USER]
        )
        logger.info(f"✅ Default admin user created: {admin_user.username}")
    except RegistrationError:
        logger.info("ℹ️  Admin user already exists")
    
    # Create a test user
    try:
        test_user = await auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="test123"
        )
        logger.info(f"✅ Test user created: {test_user.username}")
    except RegistrationError:
        logger.info("ℹ️  Test user already exists")
