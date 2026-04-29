# type: ignore
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..db import get_db
from ..auth.dependencies import require_admin, get_current_user
from ..services.user_service import UserService
from ..schemas.users import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, 
    UserSearch, PasswordReset
)
from ..models.users import User, UserRole, UserStatus
import uuid
from pathlib import Path
from datetime import datetime
import os
from sqlalchemy.exc import IntegrityError

router = APIRouter()


@router.get("/search", response_model=Dict[str, Any])
async def search_users(
    search: str = Query(None, description="Search term for username, email, or full name"),
    role: Optional[str] = Query(None, description="Filter by user role"),
    status: Optional[str] = Query(None, description="Filter by user status"),
    skip: int = Query(0, ge=0, description="Skip number of records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit number of records"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Convert string to enum if valid, else None
    role_enum = UserRole(role) if role in UserRole.__members__ else None
    status_enum = UserStatus(status) if status in UserStatus.__members__ else None
    search_params = UserSearch(
        search=search,
        role=role_enum,
        status=status_enum,
        skip=skip,
        limit=limit
    )
    user_service = UserService(db)
    result = user_service.search_users(search_params)
    result["users"] = [UserListResponse.model_validate(u) for u in result["users"]]
    return result


@router.get("/", response_model=Dict[str, List[UserListResponse]])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None, description="Filter by user role"),
    status: Optional[str] = Query(None, description="Filter by user status"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    valid_roles = ("ADMIN", "MANAGER", "USER")
    valid_statuses = ("ACTIVE", "INACTIVE", "SUSPENDED")
    role_value = role if (role and role in valid_roles) else None
    status_value = status if (status and status in valid_statuses) else None
    filters = []
    if role_value:
        # Accept both string and enum for compatibility
        try:
            enum_role = UserRole(role_value) if not role_value.startswith('UserRole.') else getattr(UserRole, role_value.split('.')[-1])
        except Exception:
            enum_role = role_value
        filters.append((User.role == role_value) | (User.role == enum_role))
    if status_value:
        filters.append(User.status == status_value)
    users_query = db.query(User)
    if filters:
        users_query = users_query.filter(*filters)
    users = users_query.offset(skip).limit(limit).all()
    return {"users": users}


@router.get("/messaging", response_model=List[UserListResponse])
async def get_users_for_messaging(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of active users for messaging purposes (excludes current user)"""
    users = db.query(User).filter(
        User.status == UserStatus.ACTIVE,
        User.id != current_user.id
    ).all()
    return [UserListResponse.model_validate(user) for user in users]


@router.get("/stats", response_model=Dict[str, Any])
async def get_user_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get user statistics (admin only)"""
    user_service = UserService(db)
    return user_service.get_user_stats()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Always reload user from DB to ensure all fields are present
    user = db.query(User).filter(User.id == current_user.id).first()
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    # Only allow updating certain fields for current user
    allowed_fields = ['email', 'full_name']
    update_data = {k: v for k, v in user_data.dict(exclude_unset=True).items() if k in allowed_fields}
    user = user_service.update_user(current_user.id, UserUpdate(**update_data))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Reload user from DB to ensure all fields are present
    user = db.query(User).filter(User.id == current_user.id).first()
    return UserResponse.model_validate(user)


@router.post("/me/upload-photo")
async def upload_current_user_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile photo for current user"""
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Validate file size (max 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path(os.environ.get("PROFILE_PHOTOS_DIR", "uploads/profile_photos"))
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, PNG, GIF, and WebP files are allowed"
        )
    
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = uploads_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update user's profile image path
    relative_path = f"uploads/profile_photos/{unique_filename}"
    current_user.profile_image = relative_path
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Profile photo uploaded successfully",
        "profile_image": relative_path
    }


@router.post("/me/change-password")
async def change_current_user_password(
    password_data: PasswordReset,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user password"""
    user_service = UserService(db)
    
    success = user_service.change_password(
        current_user.id, 
        password_data.current_password, 
        password_data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return {"message": "Password changed successfully"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new user (admin only)"""
    user_service = UserService(db)
    try:
        new_user = user_service.create_user(user_data)
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    user_service = UserService(db)
    
    # Get user info before update for logging
    user_before_update = user_service.get_user_by_id(user_id)
    if not user_before_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = user_service.update_user(user_id, user_data)  # type: ignore
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted permanently"}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Activate user (admin only)"""
    user_service = UserService(db)
    
    # Get user info for logging
    user_to_activate = user_service.get_user_by_id(user_id)
    if not user_to_activate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = user_service.activate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User activated successfully"}


@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Suspend user (admin only)"""
    user_service = UserService(db)
    
    # Get user info for logging
    user_to_suspend = user_service.get_user_by_id(user_id)
    if not user_to_suspend:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = user_service.suspend_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User suspended successfully"}


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    password_data: PasswordReset,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reset user password (admin only)"""
    user_service = UserService(db)
    
    # Get user info for logging
    user_to_reset = user_service.get_user_by_id(user_id)
    if not user_to_reset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = user_service.reset_password(user_id, password_data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Password reset successfully"}


@router.post("/{user_id}/upload-photo")
async def upload_profile_photo(
    user_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Upload profile photo for user (admin only)"""
    # Check if user exists
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path(os.environ.get("PROFILE_PHOTOS_DIR", "uploads/profile_photos"))
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = uploads_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update user's profile image path
    relative_path = f"uploads/profile_photos/{unique_filename}"
    user.profile_image = relative_path
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Profile photo uploaded successfully",
        "profile_image": relative_path
    } 