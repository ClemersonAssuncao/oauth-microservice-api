"""
Dependency Injection Container
"""
from infraestructure.config.settings import get_settings
from infraestructure.crypto.rsa_manager import RSAKeyManager
from infraestructure.database import Database
from infraestructure.repositories.sqlite_user_repository import SQLiteUserRepository
from application.auth_service import AuthenticationService


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
            
            # Initialize repository with database session factory
            self.user_repository = SQLiteUserRepository(
                session_factory=self.database.get_session
            )
            
            # Initialize authentication service
            self.auth_service = AuthenticationService(
                user_repository=self.user_repository,
                private_key=self.rsa_manager.load_private_key(),
                public_key=self.rsa_manager.load_public_key(),
                algorithm=self.settings.jwt_algorithm,
                access_token_expire_minutes=self.settings.jwt_expiration_minutes,
                refresh_token_expire_days=self.settings.refresh_token_expiration_days
            )
            
            Container._initialized = True
