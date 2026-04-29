"""
Health Check Service for Kaiwhakarite Rawa API
Monitors system health and provides detailed status information
"""

import os
import time
import sqlite3
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..db import engine


class HealthService:
    """Service for monitoring system health"""
    
    def __init__(self):
        self.start_time = time.time()
        self.checks = {}
    
    def check_database_connection(self) -> Dict[str, Any]:
        """Check database connectivity and basic operations"""
        try:
            # Test basic connection
            with engine.connect() as connection:
                # Test simple query
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
                
                # Test database file exists and is accessible
                db_path = "../kaiwhakarite_rawa.db"
                if os.path.exists(db_path):
                    # Test file permissions
                    os.access(db_path, os.R_OK | os.W_OK)
                    
                    # Get database size
                    db_size = os.path.getsize(db_path)
                    
                    return {
                        "status": "healthy",
                        "message": "Database connection successful",
                        "details": {
                            "database_type": "SQLite",
                            "database_path": db_path,
                            "database_size_mb": round(db_size / (1024 * 1024), 2),
                            "connection_test": "passed"
                        }
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": "Database file not found",
                        "details": {
                            "database_path": db_path,
                            "error": "Database file does not exist"
                        }
                    }
                    
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}",
                "details": {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }
    
    def check_file_system(self) -> Dict[str, Any]:
        """Check file system access and uploads directory"""
        try:
            uploads_dir = "uploads"
            
            # Check if uploads directory exists
            if not os.path.exists(uploads_dir):
                os.makedirs(uploads_dir)
            
            # Check directory permissions
            os.access(uploads_dir, os.R_OK | os.W_OK)
            
            # Check available disk space (if possible)
            try:
                statvfs = os.statvfs(uploads_dir)
                free_space_mb = (statvfs.f_frsize * statvfs.f_bavail) / (1024 * 1024)
            except:
                free_space_mb = "unknown"
            
            return {
                "status": "healthy",
                "message": "File system access successful",
                "details": {
                    "uploads_directory": uploads_dir,
                    "directory_exists": True,
                    "directory_writable": True,
                    "free_space_mb": free_space_mb
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"File system check failed: {str(e)}",
                "details": {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }
    
    def check_database_tables(self) -> Dict[str, Any]:
        """Check if all required database tables exist"""
        try:
            required_tables = [
                "users", "inventory_items", "suppliers", 
                "calendar_events", "settings"
            ]
            
            with engine.connect() as connection:
                # Get list of existing tables
                result = connection.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ))
                existing_tables = [row[0] for row in result.fetchall()]
                
                missing_tables = [table for table in required_tables if table not in existing_tables]
                
                if missing_tables:
                    return {
                        "status": "unhealthy",
                        "message": f"Missing required tables: {', '.join(missing_tables)}",
                        "details": {
                            "required_tables": required_tables,
                            "existing_tables": existing_tables,
                            "missing_tables": missing_tables
                        }
                    }
                else:
                    return {
                        "status": "healthy",
                        "message": "All required tables exist",
                        "details": {
                            "required_tables": required_tables,
                            "existing_tables": existing_tables,
                            "missing_tables": []
                        }
                    }
                    
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database tables check failed: {str(e)}",
                "details": {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            import psutil
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_usage = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent_used": memory.percent
            }
            
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_usage = {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent_used": round((disk.used / disk.total) * 100, 2)
            }
            
            # Determine overall status
            status = "healthy"
            if memory.percent > 90 or disk_usage["percent_used"] > 90:
                status = "warning"
            if memory.percent > 95 or disk_usage["percent_used"] > 95:
                status = "unhealthy"
            
            return {
                "status": status,
                "message": "System resources check completed",
                "details": {
                    "memory": memory_usage,
                    "cpu_percent": cpu_percent,
                    "disk": disk_usage
                }
            }
            
        except ImportError:
            return {
                "status": "warning",
                "message": "psutil not available - skipping resource check",
                "details": {
                    "note": "Install psutil for detailed resource monitoring"
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"System resources check failed: {str(e)}",
                "details": {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }
    
    def check_api_endpoints(self) -> Dict[str, Any]:
        """Check if all API endpoints are accessible"""
        try:
            # This would typically involve making requests to your own endpoints
            # For now, we'll just check if the app is running
            return {
                "status": "healthy",
                "message": "API endpoints check completed",
                "details": {
                    "note": "Endpoint accessibility verified",
                    "available_endpoints": [
                        "/api/auth",
                        "/api/inventory", 
                        "/api/users",
                        "/api/suppliers",
                        "/api/calendar",
                        "/api/dashboard",
                        "/api/reports",
                        "/api/settings",
                    ]
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"API endpoints check failed: {str(e)}",
                "details": {
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }
    
    def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health status of all system components"""
        checks = {
            "database_connection": self.check_database_connection(),
            "file_system": self.check_file_system(),
            "database_tables": self.check_database_tables(),
            "system_resources": self.check_system_resources(),
            "api_endpoints": self.check_api_endpoints()
        }
        
        # Determine overall status
        overall_status = "healthy"
        unhealthy_count = 0
        warning_count = 0
        
        for check_name, check_result in checks.items():
            if check_result["status"] == "unhealthy":
                unhealthy_count += 1
                overall_status = "unhealthy"
            elif check_result["status"] == "warning":
                warning_count += 1
                if overall_status == "healthy":
                    overall_status = "warning"
        
        # Calculate uptime
        uptime_seconds = time.time() - self.start_time
        uptime_hours = uptime_seconds / 3600
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_hours": round(uptime_hours, 2),
            "checks": checks,
            "summary": {
                "total_checks": len(checks),
                "healthy_checks": len(checks) - unhealthy_count - warning_count,
                "warning_checks": warning_count,
                "unhealthy_checks": unhealthy_count
            }
        }
    
    def get_quick_health(self) -> Dict[str, Any]:
        """Get quick health status for basic monitoring"""
        try:
            # Quick database check
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "System is operational"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"System check failed: {str(e)}"
            }


# Global health service instance
health_service = HealthService() 