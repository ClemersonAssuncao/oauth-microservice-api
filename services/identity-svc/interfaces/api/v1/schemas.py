"""
Pydantic models/schemas for API v1
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional


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


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenIntrospectionResponse(BaseModel):
    active: bool
    sub: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    roles: Optional[List[str]] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
