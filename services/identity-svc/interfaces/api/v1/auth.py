"""
Authentication and OAuth 2.1 endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import logging

from interfaces.api.v1.schemas import (
    TokenResponse,
    RefreshTokenRequest,
    TokenIntrospectionResponse,
    UserResponse
)
from interfaces.api.dependencies import get_current_user
from interfaces.api.container import Container
from application.auth_service import AuthenticationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
container = Container()


@router.post("/token", response_model=TokenResponse)
async def oauth_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth 2.1 Token endpoint
    Supports password grant type
    """
    try:
        tokens = await container.auth_service.login(
            username=form_data.username,
            password=form_data.password
        )
        logger.info(f"User {form_data.username} authenticated successfully")
        return tokens
    except AuthenticationError as e:
        logger.warning(f"Authentication failed for user {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=TokenResponse)
async def oauth_refresh(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        access_token = await container.auth_service.refresh_access_token(request.refresh_token)
        return {
            "access_token": access_token,
            "refresh_token": request.refresh_token,  # Keep same refresh token
            "token_type": "Bearer",
            "expires_in": container.settings.jwt_expiration_minutes * 60
        }
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/introspect", response_model=TokenIntrospectionResponse)
async def oauth_introspect(token: str):
    """Token introspection endpoint"""
    try:
        payload = await container.auth_service.verify_token(token)
        return TokenIntrospectionResponse(
            active=True,
            sub=payload.get("sub"),
            username=payload.get("username"),
            email=payload.get("email"),
            roles=payload.get("roles"),
            exp=payload.get("exp"),
            iat=payload.get("iat")
        )
    except AuthenticationError:
        return TokenIntrospectionResponse(active=False)


@router.get("/userinfo", response_model=UserResponse)
async def oauth_userinfo(current_user = Depends(get_current_user)):
    """OAuth UserInfo endpoint"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        roles=[role.value for role in current_user.roles],
        is_active=current_user.is_active
    )
