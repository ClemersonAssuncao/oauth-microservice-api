"""
User management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from interfaces.api.v1.schemas import (
    UserRegisterRequest,
    UserResponse
)
from interfaces.api.dependencies import get_current_user
from interfaces.api.container import Container
from application.auth_service import RegistrationError
from domain.entities.user import UserRole

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])
container = Container()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegisterRequest):
    """Register a new user"""
    try:
        user = await container.auth_service.register_user(
            username=request.username,
            email=request.email,
            password=request.password
        )
        logger.info(f"New user registered: {user.username}")
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            roles=[role.value for role in user.roles],
            is_active=user.is_active
        )
    except RegistrationError as e:
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current authenticated user info"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        roles=[role.value for role in current_user.roles],
        is_active=current_user.is_active
    )


@router.get("", response_model=List[UserResponse])
async def list_users(current_user = Depends(get_current_user)):
    """List all users (admin only)"""
    # Check if user is admin
    if UserRole.ADMIN not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = await container.user_repository.list_all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            roles=[role.value for role in user.roles],
            is_active=user.is_active
        )
        for user in users
    ]
