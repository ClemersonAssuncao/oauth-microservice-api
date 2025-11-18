"""
User-related Pydantic schemas
"""
from pydantic import BaseModel, EmailStr
from typing import List


class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    roles: List[str]
    is_active: bool
