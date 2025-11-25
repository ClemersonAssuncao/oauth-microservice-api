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
from interfaces.api.container import Container
from application.commands.login_command import LoginCommand, AuthenticationError
from application.commands.create_token_command import CreateTokenCommand
from application.commands.verify_and_refresh_token_command import (
    VerifyAndRefreshTokenCommand,
    TokenVerificationError
)

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
        # Authenticate user
        login_command = LoginCommand(
            username=form_data.username,
            password=form_data.password
        )
        login_result = await container.command_bus.dispatch(login_command)
        
        # Create access token
        access_token_command = CreateTokenCommand(
            user=login_result.user,
            token_type="access"
        )
        access_token_result = await container.command_bus.dispatch(access_token_command)
        
        # Create refresh token
        refresh_token_command = CreateTokenCommand(
            user=login_result.user,
            token_type="refresh"
        )
        refresh_token_result = await container.command_bus.dispatch(refresh_token_command)
        
        logger.info(f"User {form_data.username} authenticated successfully")
        return TokenResponse(
            access_token=access_token_result.token,
            refresh_token=refresh_token_result.token,
            token_type=access_token_result.token_type,
            expires_in=access_token_result.expires_in
        )
    except AuthenticationError as e:
        logger.warning(f"Authentication failed for user {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    try:
        command = VerifyAndRefreshTokenCommand(
            refresh_token=request.refresh_token
        )
        result = await container.command_bus.dispatch(command)
        
        logger.info("Token refreshed successfully")
        return TokenResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            token_type=result.token_type,
            expires_in=result.expires_in
        )
    except TokenVerificationError as e:
        logger.warning(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

