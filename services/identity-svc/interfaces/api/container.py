"""
Dependency Injection Container
"""
from infraestructure.config.settings import get_settings
from infraestructure.crypto.rsa_manager import RSAKeyManager
from infraestructure.database import Database
from infraestructure.repositories.sqlite_user_repository import SQLiteUserRepository

from application.commands.execute.command_bus import CommandBus
from application.commands.register_user_command import (
    RegisterUserCommand,
    RegisterUserCommandHandler
)
from application.commands.login_command import (
    LoginCommand,
    LoginCommandHandler
)
from application.commands.create_token_command import (
    CreateTokenCommand,
    CreateTokenCommandHandler
)
from application.commands.refresh_token_command import (
    RefreshTokenCommand,
    RefreshTokenCommandHandler
)


class Container:
    """Dependency injection container (Singleton)"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not Container._initialized:
            # Initialize settings
            self.settings = get_settings()
            
            # Initialize database
            self.database = Database(database_url=self.settings.database_url)
            
            # Initialize RSA key manager
            self.rsa_manager = RSAKeyManager(keys_dir=self.settings.keys_directory)
            self.rsa_manager.ensure_keys_exist()
            private_key = self.rsa_manager.load_private_key()
            
            # Initialize repository with database session factory
            self.user_repository = SQLiteUserRepository(
                session_factory=self.database.get_session
            )

             # Command Handlers
            self.register_user_handler = RegisterUserCommandHandler(self.user_repository)
            self.login_handler = LoginCommandHandler(self.user_repository)
            self.create_token_handler = CreateTokenCommandHandler(
                private_key=private_key,
                algorithm=self.settings.jwt_algorithm,
                access_token_expire_minutes=self.settings.jwt_expiration_minutes,
                refresh_token_expire_days=self.settings.refresh_token_expiration_days
            )
            self.refresh_token_handler = RefreshTokenCommandHandler(
                private_key=private_key,
                algorithm=self.settings.jwt_algorithm,
                access_token_expire_minutes=self.settings.jwt_expiration_minutes,
                refresh_token_expire_days=self.settings.refresh_token_expiration_days
            )
            
            # Initialize command bus
            self.command_bus = CommandBus()
            self.command_bus.register(RegisterUserCommand, self.register_user_handler)
            self.command_bus.register(LoginCommand, self.login_handler)
            self.command_bus.register(CreateTokenCommand, self.create_token_handler)
            self.command_bus.register(RefreshTokenCommand, self.refresh_token_handler)
            
            Container._initialized = True
