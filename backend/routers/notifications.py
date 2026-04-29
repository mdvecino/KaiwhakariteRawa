from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..db import get_db
from ..auth.dependencies import get_current_user
from ..models.users import User
from ..services.notification_service import NotificationService
from ..schemas.notifications import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationTemplateCreate, NotificationTemplateUpdate, NotificationTemplateResponse,
    UserNotificationPreferences, NotificationStats, BulkNotificationCreate
)

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def get_user_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for the current user"""
    notification_service = NotificationService(db)
    notifications = notification_service.get_user_notifications(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    return notifications


@router.get("/unread", response_model=List[NotificationResponse])
async def get_unread_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unread notifications for the current user"""
    notification_service = NotificationService(db)
    notifications = notification_service.get_unread_notifications(user_id=current_user.id)
    return notifications


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification statistics for the current user"""
    notification_service = NotificationService(db)
    stats = notification_service.get_notification_stats(user_id=current_user.id)
    return stats


@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new notification"""
    notification_service = NotificationService(db)
    notification = notification_service.create_notification(notification_data)
    return notification


@router.post("/bulk", response_model=List[NotificationResponse])
async def create_bulk_notifications(
    bulk_data: BulkNotificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create multiple notifications for different recipients"""
    notification_service = NotificationService(db)
    notifications = notification_service.create_bulk_notifications(bulk_data)
    return notifications


@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    notification_service = NotificationService(db)
    success = notification_service.mark_as_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}


@router.put("/read-all")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the current user"""
    notification_service = NotificationService(db)
    count = notification_service.mark_all_as_read(current_user.id)
    return {"message": f"{count} notifications marked as read"}


@router.get("/preferences", response_model=UserNotificationPreferences)
async def get_user_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification preferences for the current user"""
    return UserNotificationPreferences(
        email_notifications=current_user.email_notifications,
        sms_notifications=current_user.sms_notifications,
        push_notifications=current_user.push_notifications,
        low_stock_alerts=current_user.low_stock_alerts,
        cultural_event_alerts=current_user.cultural_event_alerts,
        system_alerts=current_user.system_alerts,
        notification_frequency=current_user.notification_frequency,
        phone_number=current_user.phone_number
    )


@router.put("/preferences", response_model=UserNotificationPreferences)
async def update_user_notification_preferences(
    preferences: UserNotificationPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences for the current user"""
    # Update user preferences
    current_user.email_notifications = preferences.email_notifications
    current_user.sms_notifications = preferences.sms_notifications
    current_user.push_notifications = preferences.push_notifications
    current_user.low_stock_alerts = preferences.low_stock_alerts
    current_user.cultural_event_alerts = preferences.cultural_event_alerts
    current_user.system_alerts = preferences.system_alerts
    current_user.notification_frequency = preferences.notification_frequency
    current_user.phone_number = preferences.phone_number
    
    db.commit()
    db.refresh(current_user)
    
    return preferences


# Admin endpoints for managing notification templates
@router.get("/templates", response_model=List[NotificationTemplateResponse])
async def get_notification_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all notification templates (Admin only)"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access notification templates"
        )
    
    from ..models.notifications import NotificationTemplate
    templates = db.query(NotificationTemplate).filter(
        NotificationTemplate.is_active == True
    ).all()
    return templates


@router.post("/templates", response_model=NotificationTemplateResponse)
async def create_notification_template(
    template_data: NotificationTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new notification template (Admin only)"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create notification templates"
        )
    
    from ..models.notifications import NotificationTemplate
    template = NotificationTemplate(**template_data.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.put("/templates/{template_id}", response_model=NotificationTemplateResponse)
async def update_notification_template(
    template_id: int,
    template_data: NotificationTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a notification template (Admin only)"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update notification templates"
        )
    
    from ..models.notifications import NotificationTemplate
    template = db.query(NotificationTemplate).filter(
        NotificationTemplate.id == template_id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification template not found"
        )
    
    # Update only provided fields
    update_data = template_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template


# Special endpoints for specific notification types
@router.post("/low-stock-alert/{item_id}")
async def create_low_stock_alert(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create low stock alert for a specific item"""
    from ..models.inventory import InventoryItem
    
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    notification_service = NotificationService(db)
    notifications = notification_service.create_low_stock_alert(item)
    
    return {
        "message": f"Low stock alert created for {item.name}",
        "notifications_sent": len(notifications)
    }


@router.post("/cultural-event-reminder")
async def create_cultural_event_reminder(
    event_title: str,
    event_date: datetime,
    user_ids: List[int],
    cultural_context: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create cultural event reminder notifications"""
    notification_service = NotificationService(db)
    notifications = notification_service.create_cultural_event_reminder(
        event_title=event_title,
        event_date=event_date,
        user_ids=user_ids,
        cultural_context=cultural_context
    )
    
    return {
        "message": f"Cultural event reminder created for {event_title}",
        "notifications_sent": len(notifications)
    }


# Test endpoint for notification system
@router.post("/test")
async def test_notification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a test notification to the current user"""
    notification_data = NotificationCreate(
        title="Test Notification",
        message="This is a test notification from Kaiwhakarite Rawa system.",
        notification_type="general",
        priority="medium",
        recipient_id=current_user.id,
        cultural_context="This test notification helps ensure the notification system is working properly for cultural resource management."
    )
    
    notification_service = NotificationService(db)
    notification = notification_service.create_notification(notification_data)
    
    return {
        "message": "Test notification sent",
        "notification_id": notification.id
    } 