"""
SQLAlchemy database models
"""
from sqlalchemy import Column, String, Boolean, Table
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Association table for user roles (many-to-many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String, primary_key=True),
    Column("role", String, primary_key=True),
)


class UserModel(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, username={self.username}, email={self.email})>"
