"""
Command: Create JWT tokens
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List
from jose import jwt

from application.commands.base.Command import Command, CommandHandler
from domain.entities.user import User


@dataclass
class CreateTokenCommand(Command):
    """Command to create JWT tokens"""
    user: User
    token_type: str  # "access" or "refresh"
    scopes: Optional[List[str]] = None


@dataclass
class CreateTokenResult:
    """Result of token creation"""
    token: str
    expires_in: int
    token_type: str

class CreateTokenCommandHandler(CommandHandler[CreateTokenCommand, CreateTokenResult]):
    """Handler for creating JWT tokens"""

    def __init__(
        self, 
        private_key: str, 
        algorithm: str = "RS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.private_key = private_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def _create_token(self, data: dict, expires_delta: timedelta) -> str:
        """Create a JWT token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
        })
        
        return jwt.encode(to_encode, self.private_key, algorithm=self.algorithm)

    async def handle(self, command: CreateTokenCommand) -> CreateTokenResult:
        """Create a JWT token
        
        Args:
            command (CreateTokenCommand): Command containing token creation data
            
        Returns:
            CreateTokenResult: Result of the token creation
        """
        if command.token_type == "access":
            data = {
                "sub": command.user.id,
                "username": command.user.username,
                "email": command.user.email,
                "roles": [role.value for role in command.user.roles],
                "scopes": command.scopes or ["read", "write"],
                "type": "access_token"
            }
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)
            expires_in = self.access_token_expire_minutes * 60
        else:  # refresh token
            data = {
                "sub": command.user.id,
                "type": "refresh_token"
            }
            expires_delta = timedelta(days=self.refresh_token_expire_days)
            expires_in = self.refresh_token_expire_days * 24 * 60 * 60

        token = self._create_token(data, expires_delta)

        return CreateTokenResult(
            token=token,
            expires_in=expires_in,
            token_type="Bearer"
        )