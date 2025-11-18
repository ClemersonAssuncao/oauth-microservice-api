"""
Infrastructure layer - In-memory User Repository Implementation
Simple implementation for development/testing
"""
from typing import Optional, List, Dict
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    """In-memory implementation of UserRepository"""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._username_index: Dict[str, str] = {}  # username -> user_id
        self._email_index: Dict[str, str] = {}  # email -> user_id
    
    async def create(self, user: User) -> User:
        """Create a new user"""
        self._users[user.id] = user
        self._username_index[user.username] = user.id
        self._email_index[user.email] = user.id
        return user
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self._users.get(user_id)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        user_id = self._username_index.get(username)
        if user_id:
            return self._users.get(user_id)
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_id = self._email_index.get(email)
        if user_id:
            return self._users.get(user_id)
        return None
    
    async def update(self, user: User) -> User:
        """Update existing user"""
        if user.id in self._users:
            # Update indexes if username or email changed
            old_user = self._users[user.id]
            
            if old_user.username != user.username:
                del self._username_index[old_user.username]
                self._username_index[user.username] = user.id
            
            if old_user.email != user.email:
                del self._email_index[old_user.email]
                self._email_index[user.email] = user.id
            
            self._users[user.id] = user
        return user
    
    async def delete(self, user_id: str) -> bool:
        """Delete user by ID"""
        user = self._users.get(user_id)
        if user:
            del self._users[user_id]
            del self._username_index[user.username]
            del self._email_index[user.email]
            return True
        return False
    
    async def list_all(self) -> List[User]:
        """List all users"""
        return list(self._users.values())
    
    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        return username in self._username_index
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if email exists"""
        return email in self._email_index
