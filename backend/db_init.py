#!/usr/bin/env python3
"""
Database initialization script for Kaiwhakarite Rawa
This script creates all necessary tables and ensures proper schema.
"""

import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.base import BaseModel
from ..models.users import User
from ..models.suppliers import Supplier
from ..db import DATABASE_URL
from werkzeug.security import generate_password_hash
import logging


def init_database():
    """Initialize the database with proper schema"""
    logging.info("🔧 Initializing database...")
    
    # Create engine and tables
    engine = create_engine(DATABASE_URL, echo=True)
    
    # Drop and recreate all tables to ensure clean schema
    BaseModel.metadata.drop_all(bind=engine)
    BaseModel.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create default admin user if not exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@kaiwhakarite.nz",
                full_name="System Administrator",
                hashed_password=generate_password_hash("admin123"),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            logging.info("✅ Created default admin user")
        
        # Create default suppliers if not exist
        suppliers_data = [
            {"name": "Māori Arts & Crafts Ltd", "contact_person": "Kiri Tane", "email": "kiri@maoriarts.co.nz", "phone": "09-123-4567"},
            {"name": "Cultural Supplies NZ", "contact_person": "James Wilson", "email": "james@culturalsupplies.nz", "phone": "09-234-5678"},
            {"name": "Traditional Materials", "contact_person": "Sarah Brown", "email": "sarah@tradmat.co.nz", "phone": "09-345-6789"},
            {"name": "Jennifer Products", "contact_person": "Jennifer Smith", "email": "jennifer@products.co.nz", "phone": "09-456-7890"},
            {"name": "Office Supplies Direct", "contact_person": "Mike Johnson", "email": "mike@officesupplies.co.nz", "phone": "09-567-8901"}
        ]
        
        for supplier_data in suppliers_data:
            existing_supplier = db.query(Supplier).filter(Supplier.name == supplier_data["name"]).first()
            if not existing_supplier:
                supplier = Supplier(**supplier_data)
                db.add(supplier)
                logging.info(f"✅ Created supplier: {supplier_data['name']}")
        
        db.commit()
        logging.info("✅ Database initialized successfully")
        
    except Exception as e:
        logging.error(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def check_database_schema():
    """Check and report database schema"""
    logging.info("🔍 Checking database schema...")
    
    conn = sqlite3.connect('../kaiwhakarite_rawa.db')
    cursor = conn.cursor()
    
    # Check all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    logging.info(f"📊 Found {len(tables)} tables:")
    for table in tables:
        logging.info(f"  - {table[0]}")
    
    # Check inventory_items table structure
    cursor.execute("PRAGMA table_info(inventory_items)")
    columns = cursor.fetchall()
    logging.info(f"\n📋 inventory_items table has {len(columns)} columns:")
    for col in columns:
        logging.info(f"  - {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    init_database()
    check_database_schema() 