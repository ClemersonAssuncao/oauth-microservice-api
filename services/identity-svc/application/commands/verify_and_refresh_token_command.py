"""
Command: Verify and refresh access token
"""
from dataclasses import dataclass
from jose import jwt, JWTError

from application.commands.base.Command import Command, CommandHandler
from application.commands.create_token_command import CreateTokenCommand, CreateTokenCommandHandler
from domain.repositories.user_repository import UserRepository


class TokenVerificationError(Exception):
    """Raised when token verification fails"""
    pass


@dataclass
class VerifyAndRefreshTokenCommand(Command):
    """Command to verify refresh token and create new access token"""
    refresh_token: str


@dataclass
class VerifyAndRefreshTokenResult:
    """Result of token refresh"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class VerifyAndRefreshTokenCommandHandler(CommandHandler[VerifyAndRefreshTokenCommand, VerifyAndRefreshTokenResult]):
    """Handler for verifying and refreshing tokens"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        create_token_handler: CreateTokenCommandHandler,
        public_key: str,
        algorithm: str = "RS256",
        access_token_expire_minutes: int = 30
    ):
        self.user_repository = user_repository
        self.create_token_handler = create_token_handler
        self.public_key = public_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
    
    async def handle(self, command: VerifyAndRefreshTokenCommand) -> VerifyAndRefreshTokenResult:
        """Verify refresh token and create new access token
        
        Args:
            command (VerifyAndRefreshTokenCommand): Command containing refresh token
            
        Returns:
            VerifyAndRefreshTokenResult: New access token and same refresh token
            
        Raises:
            TokenVerificationError: If token is invalid or user not found
        """
        try:
            # Verify and decode refresh token
            payload = jwt.decode(
                command.refresh_token,
                self.public_key,
                algorithms=[self.algorithm]
            )
            
            # Check token type
            if payload.get("type") != "refresh_token":
                raise TokenVerificationError("Invalid token type")
            
            # Get user
            user_id = payload.get("sub")
            if not user_id:
                raise TokenVerificationError("Invalid token payload")
            
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise TokenVerificationError("User not found")
            
            if not user.is_active:
                raise TokenVerificationError("User account is inactive")
            
            # Create new access token
            access_token_command = CreateTokenCommand(
                user=user,
                token_type="access"
            )
            access_token_result = await self.create_token_handler.handle(access_token_command)
            
            return VerifyAndRefreshTokenResult(
                access_token=access_token_result.token,
                refresh_token=command.refresh_token,  # Keep same refresh token
                token_type=access_token_result.token_type,
                expires_in=access_token_result.expires_in
            )
            
        except JWTError as e:
            raise TokenVerificationError(f"Invalid refresh token: {str(e)}")
