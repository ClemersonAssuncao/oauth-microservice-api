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
class RefreshTokenCommand(Command):
    """Command to create JWT tokens"""
    user: User
    token_type: str  # "access" or "refresh"
    scopes: Optional[List[str]] = None


@dataclass
class RefreshTokenResult:
    """Result of token creation"""
    token: str
    expires_in: int
    token_type: str

class RefreshTokenCommandHandler(CommandHandler[RefreshTokenCommand, RefreshTokenResult]):
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

    async def handle(self, command: RefreshTokenCommand) -> RefreshTokenResult:
        """Create a JWT token
        
        Args:
            command (RefreshTokenCommand): Command containing token creation data
            
        Returns:
            RefreshTokenResult: Result of the token creation
        """
        data = {
            "sub": command.user.id,
            "type": "refresh_token"
        }

        expires_delta = timedelta(days=self.refresh_token_expire_days)
        expires_in = self.refresh_token_expire_days * 24 * 60 * 60

        token = self._create_token(data, expires_delta)

        return RefreshTokenResult(
            token=token,
            expires_in=expires_in,
            token_type="Bearer"
        )