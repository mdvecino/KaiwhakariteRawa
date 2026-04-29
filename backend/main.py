from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

# Configure logging for the backend
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

# Import routers
from backend.routers import (
    auth, inventory, users, suppliers, calendar, 
    dashboard, reports, settings, health, supplier_returns, customer_returns, maori_news
)
from backend.routers.customers import router as customers_router
from backend.routers.notifications import router as notifications_router
from backend.routers.messages import router as messages_router

# Import database
from backend.db import engine
from backend.models import base
from backend.services.user_service import UserService
from backend.models.users import UserRole
from backend.schemas.users import UserCreate
from sqlalchemy.orm import Session

# Create database tables
base.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Kaiwhakarite Rawa",
    description=(
        "Inventory and Resource Management System with Māori Cultural Integration"
    ),
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded images
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["Suppliers"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(health.router, prefix="/health", tags=["Health Checks"])
app.include_router(supplier_returns.router)
app.include_router(customer_returns.router, prefix="/api")
app.include_router(customers_router, prefix="/api")
app.include_router(maori_news.router, prefix="/api", tags=["Maori News"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(messages_router, prefix="/api/messages", tags=["Messages"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Kaiwhakarite Rawa",
        "version": "1.0.0",
        "description": "Inventory and Resource Management System"
    }


@app.get("/health")
async def health_check():
    """Legacy health check endpoint - redirects to new health system"""
    from backend.services.health_service import health_service
    return health_service.get_quick_health()


def seed_demo_users():
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
    for demo in demo_users:
        if not user_service.get_user_by_username(demo["username"]):
            user_data = UserCreate(**demo)
            try:
                user_service.create_user(user_data)
            except Exception as e:
                print(
                    f"Could not create demo user {demo['username']}: {e}"
                )
    session.close()
    db.close()


# Seed demo users at startup
seed_demo_users()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 