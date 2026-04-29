from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict
from ..models.users import User, UserRole, UserStatus
from ..schemas.users import UserCreate, UserUpdate, UserSearch
from ..auth.auth_handler import get_password_hash, verify_password
from datetime import datetime
import logging
from ..services import BaseService


class UserService(BaseService[User]):
    """Service class for user management operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, User)
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if username or email already exists
        existing_user = self.db.query(User).filter(
            or_(
                User.username == user_data.username,
                User.email == user_data.email
            )
        ).first()
        
        if existing_user:
            raise ValueError("Username or email already exists")
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            status=user_data.status,
            profile_image=user_data.profile_image,
            two_factor_enabled=user_data.two_factor_enabled or False
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.get_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users with pagination"""
        return self.db.query(User).filter(
            User.status == UserStatus.ACTIVE
        ).offset(skip).limit(limit).all()
    
    def search_users(self, search_params: UserSearch) -> Dict[str, any]:
        """Search users with filtering and pagination"""
        query = self.db.query(User)

        # Debug: print search parameters
        logging.debug(f"[DEBUG] search_users called with: search={search_params.search}, role={search_params.role}, status={search_params.status}")

        # Only filter by status if status is not 'ALL' or empty
        if search_params.status and str(search_params.status).upper() != 'ALL':
            query = query.filter(User.status == search_params.status)

        # Always apply search filter if present
        if search_params.search:
            search_term = f"%{search_params.search.strip()}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    User.full_name.ilike(search_term)
                )
            )

        # Apply role filter
        if search_params.role:
            query = query.filter(User.role == search_params.role)

        # Debug: print the SQL query being executed
        logging.debug(f"[DEBUG] SQL: {str(query.statement.compile(compile_kwargs={'literal_binds': True}))}")

        # Get total count
        total = query.count()
        logging.debug(f"[DEBUG] search_users found {total} users matching criteria.")

        # Apply pagination
        users = query.offset(search_params.skip).limit(search_params.limit).all()

        return {
            "users": users,
            "total": total,
            "skip": search_params.skip,
            "limit": search_params.limit
        }
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Permanently delete a user from the database"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user by setting status to active"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.status = UserStatus.ACTIVE  # type: ignore
        user.updated_at = datetime.utcnow()  # type: ignore
        self.db.commit()
        return True
    
    def suspend_user(self, user_id: int) -> bool:
        """Suspend a user by setting status to suspended"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.status = UserStatus.SUSPENDED  # type: ignore
        user.updated_at = datetime.utcnow()  # type: ignore
        self.db.commit()
        return True
    
    def reset_password(self, user_id: int, new_password: str) -> bool:
        """Reset user password"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.hashed_password = get_password_hash(new_password)  # type: ignore
        user.updated_at = datetime.utcnow()  # type: ignore
        self.db.commit()
        return True
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password with current password verification"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Verify current password
        if not verify_password(current_password, user.hashed_password):  # type: ignore
            return False
        
        # Update password
        user.hashed_password = get_password_hash(new_password)  # type: ignore
        user.updated_at = datetime.utcnow()  # type: ignore
        self.db.commit()
        return True
    
    def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        user = self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()  # type: ignore
            self.db.commit()
    
    def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get users by role"""
        return self.db.query(User).filter(
            and_(User.role == role, User.status == UserStatus.ACTIVE)
        ).all()
    
    def change_user_role(self, user_id: int, new_role: UserRole) -> Optional[User]:
        """Change user role (admin only)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.role = new_role  # type: ignore
        user.updated_at = datetime.utcnow()  # type: ignore
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_stats(self) -> Dict[str, any]:
        """Get user statistics"""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.status == UserStatus.ACTIVE).count()
        inactive_users = self.db.query(User).filter(User.status == UserStatus.INACTIVE).count()
        suspended_users = self.db.query(User).filter(User.status == UserStatus.SUSPENDED).count()
        
        admin_count = self.db.query(User).filter(User.role == UserRole.ADMIN).count()
        manager_count = self.db.query(User).filter(User.role == UserRole.MANAGER).count()
        user_count = self.db.query(User).filter(User.role == UserRole.USER).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "suspended_users": suspended_users,
            "admin_count": admin_count,
            "manager_count": manager_count,
            "user_count": user_count
        } 