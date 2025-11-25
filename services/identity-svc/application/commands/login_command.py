"""
Command: User login
"""
from dataclasses import dataclass
from passlib.context import CryptContext

from application.commands.base.Command import Command, CommandHandler
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


@dataclass
class LoginCommand(Command):
    """Command to login a user"""
    username: str
    password: str


@dataclass
class LoginResult:
    """Result of user login"""
    user: User
    success: bool
    message: str

class LoginCommandHandler(CommandHandler[LoginCommand, LoginResult]):
    """Handler for user login"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def handle(self, command: LoginCommand) -> LoginResult:
        """Authenticate a user
        
        Args:
            command (LoginCommand): Command containing user login data
            
        Returns:
            LoginResult: Result of the user login
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # Retrieve user by username
        user = await self.user_repository.get_by_username(command.username)
        if not user:
            raise AuthenticationError("Invalid username or password")
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationError("User account is inactive")
        
        # Verify password
        if not self._verify_password(command.password, user.hashed_password):
            raise AuthenticationError("Invalid username or password")
        
        return LoginResult(
            user=user,
            success=True,
            message="User authenticated successfully"
        )