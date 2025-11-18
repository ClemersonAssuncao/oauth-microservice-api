"""
SQLite implementation of UserRepository
"""
from typing import Optional, List
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User, UserRole
from domain.repositories.user_repository import UserRepository
from infraestructure.database.models import UserModel, user_roles


class SQLiteUserRepository(UserRepository):
    """SQLite implementation of user repository using SQLAlchemy"""
    
    def __init__(self, session_factory):
        """
        Initialize repository with session factory
        
        Args:
            session_factory: AsyncSession factory from Database class
        """
        self.session_factory = session_factory
    
    async def _get_session(self) -> AsyncSession:
        """Get a new database session"""
        async for session in self.session_factory():
            return session
    
    async def save(self, user: User) -> User:
        """Save or update a user in the database"""
        session = await self._get_session()
        
        try:
            # Check if user exists
            result = await session.execute(
                select(UserModel).where(UserModel.id == user.id)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                # Update existing user
                existing_user.username = user.username
                existing_user.email = user.email
                existing_user.hashed_password = user.hashed_password
                existing_user.is_active = user.is_active
            else:
                # Create new user
                user_model = UserModel(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    hashed_password=user.hashed_password,
                    is_active=user.is_active
                )
                session.add(user_model)
            
            # Update roles - delete old ones and insert new ones
            await session.execute(
                delete(user_roles).where(user_roles.c.user_id == user.id)
            )
            
            for role in user.roles:
                await session.execute(
                    insert(user_roles).values(user_id=user.id, role=role.value)
                )
            
            await session.commit()
            return user
            
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        session = await self._get_session()
        
        try:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            # Get user roles
            roles_result = await session.execute(
                select(user_roles.c.role).where(user_roles.c.user_id == user_id)
            )
            roles = [UserRole(row[0]) for row in roles_result.fetchall()]
            
            return User(
                id=user_model.id,
                username=user_model.username,
                email=user_model.email,
                hashed_password=user_model.hashed_password,
                roles=roles,
                is_active=user_model.is_active
            )
            
        finally:
            await session.close()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        session = await self._get_session()
        
        try:
            result = await session.execute(
                select(UserModel).where(UserModel.username == username)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            # Get user roles
            roles_result = await session.execute(
                select(user_roles.c.role).where(user_roles.c.user_id == user_model.id)
            )
            roles = [UserRole(row[0]) for row in roles_result.fetchall()]
            
            return User(
                id=user_model.id,
                username=user_model.username,
                email=user_model.email,
                hashed_password=user_model.hashed_password,
                roles=roles,
                is_active=user_model.is_active
            )
            
        finally:
            await session.close()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        session = await self._get_session()
        
        try:
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return None
            
            # Get user roles
            roles_result = await session.execute(
                select(user_roles.c.role).where(user_roles.c.user_id == user_model.id)
            )
            roles = [UserRole(row[0]) for row in roles_result.fetchall()]
            
            return User(
                id=user_model.id,
                username=user_model.username,
                email=user_model.email,
                hashed_password=user_model.hashed_password,
                roles=roles,
                is_active=user_model.is_active
            )
            
        finally:
            await session.close()
    
    async def delete(self, user_id: str) -> bool:
        """Delete a user by ID"""
        session = await self._get_session()
        
        try:
            # Delete user roles first
            await session.execute(
                delete(user_roles).where(user_roles.c.user_id == user_id)
            )
            
            # Delete user
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                return False
            
            await session.delete(user_model)
            await session.commit()
            return True
            
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    
    async def list_all(self) -> List[User]:
        """List all users"""
        session = await self._get_session()
        
        try:
            result = await session.execute(select(UserModel))
            user_models = result.scalars().all()
            
            users = []
            for user_model in user_models:
                # Get user roles
                roles_result = await session.execute(
                    select(user_roles.c.role).where(user_roles.c.user_id == user_model.id)
                )
                roles = [UserRole(row[0]) for row in roles_result.fetchall()]
                
                users.append(User(
                    id=user_model.id,
                    username=user_model.username,
                    email=user_model.email,
                    hashed_password=user_model.hashed_password,
                    roles=roles,
                    is_active=user_model.is_active
                ))
            
            return users
            
        finally:
            await session.close()
    
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        session = await self._get_session()
        
        try:
            result = await session.execute(
                select(UserModel).where(UserModel.username == username)
            )
            return result.scalar_one_or_none() is not None
            
        finally:
            await session.close()
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        session = await self._get_session()
        
        try:
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            return result.scalar_one_or_none() is not None
            
        finally:
            await session.close()
