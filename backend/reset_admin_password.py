import os
import sys
from sqlalchemy.orm import sessionmaker
from ..db import engine
from ..models.users import User
from passlib.context import CryptContext

# Set up password hashing context (should match your app's context)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# New password
default_password = "admin123"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        print("No admin user found. Exiting.")
        sys.exit(1)
    
    admin_user.hashed_password = pwd_context.hash(default_password)
    db.commit()
    print("Admin password reset to 'admin123'.")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close() 