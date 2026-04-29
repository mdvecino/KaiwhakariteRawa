#!/usr/bin/env python3
"""Recreate database and seed with demo users"""

import sys
import os
sys.path.append(os.getcwd())

from backend.db import engine
from backend.models import base
from backend.services.user_service import UserService
from backend.models.users import UserRole
from backend.schemas.users import UserCreate
from sqlalchemy.orm import Session

print("🗄️  Recreating database...")

# Create database tables
base.Base.metadata.create_all(bind=engine)

def seed_demo_users():
    """Seed demo users in the database"""
    db = engine.connect()
    session = Session(bind=db)
    user_service = UserService(session)
    
    demo_users = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "full_name": "Admin User",
            "role": UserRole.ADMIN,
            "profile_image": None,
            "two_factor_enabled": False
        },
        {
            "username": "manager",
            "email": "manager@example.com",
            "password": "manager123",
            "full_name": "Manager User",
            "role": UserRole.MANAGER,
            "profile_image": None,
            "two_factor_enabled": False
        },
        {
            "username": "user",
            "email": "user@example.com",
            "password": "user123",
            "full_name": "Regular User",
            "role": UserRole.USER,
            "profile_image": None,
            "two_factor_enabled": False
        }
    ]
    
    print("👥 Creating demo users...")
    for demo in demo_users:
        if not user_service.get_user_by_username(demo["username"]):
            user_data = UserCreate(**demo)
            try:
                user_service.create_user(user_data)
                print(f"✅ Created user: {demo['username']}")
            except Exception as e:
                print(f"❌ Could not create demo user {demo['username']}: {e}")
        else:
            print(f"ℹ️  User {demo['username']} already exists")
    
    session.close()
    db.close()

if __name__ == "__main__":
    print("🚀 Starting database recreation...")
    seed_demo_users()
    print("✅ Database recreation completed!")
