from passlib.context import CryptContext
from dataclasses import dataclass
from typing import Optional, List

from application.commands.base.Command import Command, CommandHandler

from domain.entities.user import User, UserRole, UserCredentials
from domain.repositories.user_repository import UserRepository


class RegistrationError(Exception):
    """Raised when user registration fails"""
    pass

@dataclass
class RegisterUserCommand(Command):
    """Command to register a new user"""
    username: str
    email: str
    password: str
    roles: Optional[List[UserRole]] = None

@dataclass
class RegisterUserResult:
    """Result of user registration"""
    user: User
    success: bool
    message: str

class RegisterUserCommandHandler(CommandHandler[RegisterUserCommand, RegisterUserResult]):
    """Handler for registering a new user"""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)
    
    async def handle(self, command: RegisterUserCommand) -> RegisterUserResult:
        """Register a new user
        
        Args:
            command (RegisterUserCommand): Command containing user registration data
            
        Returns:
            RegisterUserResult: Result of the user registration
            
        Raises:
            RegistrationError: If registration fails
        """
        try:
            # Validate credentials
            credentials = UserCredentials(
                username=command.username,
                password=command.password
            )
            errors = credentials.validate()
            if errors:
                raise RegistrationError(f"Validation failed: {', '.join(errors)}")
            
            # Check if username exists
            if await self.user_repository.exists_by_username(command.username):
                raise RegistrationError(f"Username '{command.username}' already exists")
            
            # Check if email exists
            if await self.user_repository.exists_by_email(command.email):
                raise RegistrationError(f"Email '{command.email}' already exists")
            
            # Hash password and create user
            user = User(
                username=command.username,
                email=command.email,
                hashed_password=self._hash_password(command.password),
                roles=command.roles or [UserRole.USER]
            )

            created_user = await self.user_repository.create(user)

            return RegisterUserResult(
                user=created_user,
                success=True,
                message="User registered successfully"
            )
        except RegistrationError:
            raise
        except Exception as e:
            raise RegistrationError(f"Registration failed: {str(e)}")