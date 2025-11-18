"""
Application layer - Use cases for user authentication
Business logic orchestration
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import jwt, JWTError
from domain.entities.user import User, UserCredentials, UserRole
from domain.repositories.user_repository import UserRepository


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class RegistrationError(Exception):
    """Raised when user registration fails"""
    pass


class AuthenticationService:
    """Service for user authentication and token management"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        private_key: str,
        public_key: str,
        algorithm: str = "RS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.user_repository = user_repository
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def _create_token(self, data: dict, expires_delta: timedelta) -> str:
        """Create a JWT token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.private_key,
            algorithm=self.algorithm
        )
        return encoded_jwt
    
    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        roles: Optional[list] = None
    ) -> User:
        """Register a new user"""
        
        # Validate credentials
        credentials = UserCredentials(username=username, password=password)
        errors = credentials.validate()
        if errors:
            raise RegistrationError(f"Validation failed: {', '.join(errors)}")
        
        # Check if username exists
        if await self.user_repository.exists_by_username(username):
            raise RegistrationError(f"Username '{username}' already exists")
        
        # Check if email exists
        if await self.user_repository.exists_by_email(email):
            raise RegistrationError(f"Email '{email}' already exists")
        
        # Create user
        user = User(
            username=username,
            email=email,
            hashed_password=self._hash_password(password),
            roles=roles or [UserRole.USER]
        )
        
        return await self.user_repository.create(user)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = await self.user_repository.get_by_username(username)
        
        if not user:
            return None
        
        if not user.is_active:
            raise AuthenticationError("User account is inactive")
        
        if not self._verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def create_access_token(self, user: User, scopes: Optional[list] = None) -> str:
        """Create an access token for a user"""
        data = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [role.value for role in user.roles],
            "scopes": scopes or ["read", "write"],
            "type": "access_token"
        }
        
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        return self._create_token(data, expires_delta)
    
    async def create_refresh_token(self, user: User) -> str:
        """Create a refresh token for a user"""
        data = {
            "sub": user.id,
            "type": "refresh_token"
        }
        
        expires_delta = timedelta(days=self.refresh_token_expire_days)
        return self._create_token(data, expires_delta)
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """Create a new access token from a refresh token"""
        try:
            payload = await self.verify_token(refresh_token)
            
            if payload.get("type") != "refresh_token":
                raise AuthenticationError("Invalid token type")
            
            user_id = payload.get("sub")
            user = await self.user_repository.get_by_id(user_id)
            
            if not user:
                raise AuthenticationError("User not found")
            
            if not user.is_active:
                raise AuthenticationError("User account is inactive")
            
            return await self.create_access_token(user)
            
        except JWTError as e:
            raise AuthenticationError(f"Invalid refresh token: {str(e)}")
    
    async def login(self, username: str, password: str) -> Dict[str, str]:
        """
        Login user and return access and refresh tokens
        OAuth 2.1 password grant flow
        """
        user = await self.authenticate_user(username, password)
        
        if not user:
            raise AuthenticationError("Invalid username or password")
        
        access_token = await self.create_access_token(user)
        refresh_token = await self.create_refresh_token(user)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
