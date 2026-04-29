# type: ignore
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..db import get_db
from ..auth.auth_handler import (
    authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..auth.dependencies import get_current_user
from ..services.user_service import UserService
from ..schemas.users import UserCreate, UserResponse, Token
from ..models.users import User

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    user_service = UserService(db)
    try:
        user = user_service.create_user(user_data)
        
        # Log the registration activity
        # activity_service.log_user_activity(
        #     user_id=user.id,
        #     action="registered",
        #     resource_type="auth",
        #     resource_id=None,
        #     description=f"New user registered: {user.username} ({user.email})"
        # )
        
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user_service = UserService(db)
    user_service.update_last_login(user.id)
    
    # Log the login activity
    # activity_service = ActivityService(db)
    # activity_service.log_user_activity(
    #     user_id=user.id,
    #     action="login",
    #     resource_type="auth",
    #     resource_id=None,
    #     description=f"User logged in: {user.username}"
    # )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    try:
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }
    except Exception as e:
        print(f"Login serialization error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Login serialization error: {e}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    return UserResponse.model_validate(current_user) 