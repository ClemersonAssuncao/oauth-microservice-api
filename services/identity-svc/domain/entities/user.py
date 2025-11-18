"""
Domain layer - User entity and value objects
Core business logic for user management
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid


class UserRole(str, Enum):
    """User roles for authorization"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


@dataclass
class User:
    """User entity - aggregate root"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    hashed_password: str = ""
    roles: List[UserRole] = field(default_factory=lambda: [UserRole.USER])
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has a specific role"""
        return role in self.roles
    
    def add_role(self, role: UserRole) -> None:
        """Add a role to the user"""
        if role not in self.roles:
            self.roles.append(role)
            self.updated_at = datetime.utcnow()
    
    def remove_role(self, role: UserRole) -> None:
        """Remove a role from the user"""
        if role in self.roles:
            self.roles.remove(role)
            self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate user account"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activate user account"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary (for serialization)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "roles": [role.value for role in self.roles],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class UserCredentials:
    """Value object for user credentials"""
    username: str
    password: str
    
    def validate(self) -> List[str]:
        """Validate credentials and return list of errors"""
        errors = []
        
        if not self.username or len(self.username) < 3:
            errors.append("Username must be at least 3 characters long")
        
        if not self.password or len(self.password) < 6:
            errors.append("Password must be at least 6 characters long")
        
        return errors
