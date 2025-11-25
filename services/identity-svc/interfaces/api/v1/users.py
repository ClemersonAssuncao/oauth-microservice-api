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
from interfaces.api.container import Container
from application.commands.register_user_command import RegisterUserCommand, RegistrationError
from domain.entities.user import UserRole

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])
container = Container()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegisterRequest):
    """Register a new user"""
    try:
        command = RegisterUserCommand(
            username=request.username,
            email=request.email,
            password=request.password
        )
        result = await container.command_bus.dispatch(command)
        
        logger.info(f"New user registered: {result.user.username}")
        return UserResponse(
            id=result.user.id,
            username=result.user.username,
            email=result.user.email,
            roles=[role.value for role in result.user.roles],
            is_active=result.user.is_active
        )
    except RegistrationError as e:
        logger.warning(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
