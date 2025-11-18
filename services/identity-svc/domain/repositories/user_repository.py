"""
Domain layer - Repository interfaces
Defines contracts for data persistence
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.user import User


class UserRepository(ABC):
    """Repository interface for User entity"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update existing user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete user by ID"""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[User]:
        """List all users"""
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if email exists"""
        pass
