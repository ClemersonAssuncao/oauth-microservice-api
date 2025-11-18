"""
Identity Service - OAuth 2.1 / OpenID Connect Provider
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from interfaces.api.container import Container
from interfaces.api.v1 import auth, users, discovery
from domain.entities.user import UserRole
from application.auth_service import RegistrationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database(container: Container) -> None:
    """Initialize database tables"""
    logger.info("🗄️  Initializing database...")
    await container.database.create_tables()
    logger.info("✅ Database tables created")


async def create_default_users(container: Container) -> None:
    """Create default admin and test users"""
    # Create a default admin user for testing
    try:
        admin_user = await container.auth_service.register_user(
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
        test_user = await container.auth_service.register_user(
            username="testuser",
            email="test@example.com",
            password="test123"
        )
        logger.info(f"✅ Test user created: {test_user.username}")
    except RegistrationError:
        logger.info("ℹ️  Test user already exists")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        FastAPI: Configured application instance
    """
    # Initialize container
    container = Container()
    settings = container.settings
    
    logger.info(f"🚀 Starting {settings.service_name}")
    logger.info(f"📝 OpenID Configuration: {settings.issuer}/.well-known/openid-configuration")
    logger.info(f"🔑 JWKS endpoint: {settings.issuer}/.well-known/jwks.json")
    
    # Create FastAPI app
    app = FastAPI(
        title="Identity Service",
        description="OAuth 2.1 / OpenID Connect Provider",
        version="1.0.0"
    )
    
    # CORS middleware
    logger.info("🔒 Configuring CORS middleware")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    logger.info("📡 Registering API routers")
    app.include_router(discovery.router)
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize application on startup"""
        # TODO: Use Alembic migrations instead of create_tables in production
        await init_database(container)
        await create_default_users(container)
        logger.info(f"✅ {settings.service_name} startup complete")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        logger.info("🛑 Shutting down service...")
        await container.database.close()
        logger.info("✅ Database connection closed")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    from infraestructure.config.settings import get_settings
    
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=True
    )
