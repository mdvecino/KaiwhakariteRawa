"""
Health Check Router for Kaiwhakarite Rawa API
Provides various health check endpoints for monitoring system status
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
from ..services.health_service import health_service

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    Returns quick status for load balancers and basic monitoring
    """
    return health_service.get_quick_health()


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check endpoint
    Returns comprehensive system status including all components
    """
    return health_service.get_comprehensive_health()


@router.get("/database")
async def database_health_check() -> Dict[str, Any]:
    """
    Database-specific health check
    Returns detailed database connectivity and status information
    """
    return health_service.check_database_connection()


@router.get("/filesystem")
async def filesystem_health_check() -> Dict[str, Any]:
    """
    File system health check
    Returns file system access and storage information
    """
    return health_service.check_file_system()


@router.get("/tables")
async def database_tables_health_check() -> Dict[str, Any]:
    """
    Database tables health check
    Returns information about required database tables
    """
    return health_service.check_database_tables()


@router.get("/resources")
async def system_resources_health_check() -> Dict[str, Any]:
    """
    System resources health check
    Returns memory, CPU, and disk usage information
    """
    return health_service.check_system_resources()


@router.get("/endpoints")
async def api_endpoints_health_check() -> Dict[str, Any]:
    """
    API endpoints health check
    Returns information about available API endpoints
    """
    return health_service.check_api_endpoints()


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint
    Used by Kubernetes and other orchestration systems
    Returns 200 only if system is ready to serve traffic
    """
    health_status = health_service.get_quick_health()
    
    if health_status["status"] == "healthy":
        return {
            "status": "ready",
            "message": "System is ready to serve traffic",
            "timestamp": health_status["timestamp"]
        }
    else:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "message": "System is not ready to serve traffic",
                "timestamp": health_status["timestamp"]
            }
        )


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check endpoint
    Used by Kubernetes and other orchestration systems
    Returns 200 if the application is running (even if not ready)
    """
    return {
        "status": "alive",
        "message": "Application is running",
        "timestamp": health_service.get_quick_health()["timestamp"]
    }


@router.get("/ping")
async def ping() -> Dict[str, Any]:
    """
    Simple ping endpoint
    Returns basic response for connectivity testing
    """
    return {
        "message": "pong",
        "timestamp": health_service.get_quick_health()["timestamp"]
    }


@router.get("/status")
async def status_check() -> Dict[str, Any]:
    """
    Status check endpoint
    Returns system status with version information
    """
    health_status = health_service.get_quick_health()
    
    return {
        "status": health_status["status"],
        "message": health_status["message"],
        "timestamp": health_status["timestamp"],
        "version": "1.0.0",
        "service": "Kaiwhakarite Rawa API"
    } 