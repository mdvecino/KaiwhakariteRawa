from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..models.users import User, UserRole
from ..auth.auth_handler import get_current_user_from_credentials
from ..db import get_db


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    return await get_current_user_from_credentials(credentials, db)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role for access"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    """Require manager or admin role for access"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin access required"
        )
    return current_user


def require_user(current_user: User = Depends(get_current_user)) -> User:
    """Require any authenticated user"""
    return current_user


 