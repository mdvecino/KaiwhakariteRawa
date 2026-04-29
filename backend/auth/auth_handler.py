from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..models.users import User
from ..schemas.users import TokenData

# Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password, with lockout after 3 failed attempts for MANAGER/USER"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active. Please contact an administrator."
        )
    if not verify_password(password, user.hashed_password):
        # Only increment for MANAGER/USER
        if user.role in ["MANAGER", "USER"]:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1  # type: ignore
            if user.failed_login_attempts >= 3:  # type: ignore
                user.status = "INACTIVE"  # type: ignore
            db.commit()
        return None
    # Successful login: reset failed attempts
    if user.role in ["MANAGER", "USER"] and user.failed_login_attempts:  # type: ignore
        user.failed_login_attempts = 0  # type: ignore
        db.commit()
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        return None


def get_current_user(db: Session, token: str) -> Optional[User]:
    """Get current user from token"""
    token_data = verify_token(token)
    if token_data is None:
        return None
    user = db.query(User).filter(User.username == token_data.username).first()
    return user


async def get_current_user_from_credentials(
    credentials: HTTPAuthorizationCredentials, db: Session
) -> User:
    """Get current user from HTTP credentials"""
    token = credentials.credentials
    user = get_current_user(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user 