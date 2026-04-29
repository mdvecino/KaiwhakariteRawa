from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from ..models.users import UserRole, UserStatus


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE


class UserCreate(UserBase):
    password: str
    profile_image: Optional[str] = None
    two_factor_enabled: Optional[bool] = False


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    profile_image: Optional[str] = None
    two_factor_enabled: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    profile_image: Optional[str] = None
    two_factor_enabled: bool
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    last_login: Optional[datetime] = None
    profile_image: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserSearch(BaseModel):
    search: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    skip: int = 0
    limit: int = 100


class PasswordReset(BaseModel):
    current_password: str
    new_password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    username: Optional[str] = None 