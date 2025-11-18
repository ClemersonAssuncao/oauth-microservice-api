"""
Token-related Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, List


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
