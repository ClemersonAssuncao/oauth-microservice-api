"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from infraestructure.database.models import Base
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database configuration and session factory"""
    
    def __init__(self, database_url: str):
        """
        Initialize database connection
        
        Args:
            database_url: SQLAlchemy database URL (e.g., sqlite+aiosqlite:///./identity.db)
        """
        self.database_url = database_url
        
        # Create async engine
        # For SQLite, we use StaticPool to allow multiple connections
        self.engine = create_async_engine(
            database_url,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
            poolclass=StaticPool if "sqlite" in database_url else None,
            echo=False,  # Set to True to see SQL queries in logs
        )
        
        # Create session factory
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        logger.info(f"Database initialized with URL: {database_url}")
    
    async def create_tables(self):
        """Create all tables in the database"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    
    async def drop_tables(self):
        """Drop all tables in the database"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped")
    
    async def get_session(self) -> AsyncSession:
        """Get a new database session"""
        async with self.async_session_maker() as session:
            yield session
    
    async def close(self):
        """Close database connection"""
        await self.engine.dispose()
        logger.info("Database connection closed")
