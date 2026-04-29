from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.notifications import (
    NotificationType, NotificationPriority, NotificationStatus, NotificationChannel
)


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    recipient_id: int
    sender_id: Optional[int] = None
    scheduled_for: Optional[datetime] = None
    notification_data: Optional[str] = None
    related_item_id: Optional[int] = None
    related_event_id: Optional[int] = None
    cultural_context: Optional[str] = None
    iwi_connection: Optional[str] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    priority: Optional[NotificationPriority] = None
    status: Optional[NotificationStatus] = None
    scheduled_for: Optional[datetime] = None
    notification_data: Optional[str] = None
    cultural_context: Optional[str] = None


class NotificationResponse(NotificationBase):
    id: int
    status: NotificationStatus
    email_sent: bool
    sms_sent: bool
    push_sent: bool
    in_app_sent: bool
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NotificationTemplateBase(BaseModel):
    name: str
    title_template: str
    message_template: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    cultural_context: Optional[str] = None
    bilingual_support: bool = False
    maori_title_template: Optional[str] = None
    maori_message_template: Optional[str] = None
    variables: Optional[str] = None
    is_active: bool = True


class NotificationTemplateCreate(NotificationTemplateBase):
    pass


class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = None
    title_template: Optional[str] = None
    message_template: Optional[str] = None
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    cultural_context: Optional[str] = None
    bilingual_support: Optional[bool] = None
    maori_title_template: Optional[str] = None
    maori_message_template: Optional[str] = None
    variables: Optional[str] = None
    is_active: Optional[bool] = None


class NotificationTemplateResponse(NotificationTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserNotificationPreferences(BaseModel):
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    low_stock_alerts: bool = True
    cultural_event_alerts: bool = True
    system_alerts: bool = True
    notification_frequency: str = "immediate"
    phone_number: Optional[str] = None


class NotificationStats(BaseModel):
    total_notifications: int
    unread_notifications: int
    pending_notifications: int
    failed_notifications: int
    notifications_by_type: Dict[str, int]
    notifications_by_priority: Dict[str, int]


class BulkNotificationCreate(BaseModel):
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    recipient_ids: List[int]
    sender_id: Optional[int] = None
    scheduled_for: Optional[datetime] = None
    cultural_context: Optional[str] = None
    iwi_connection: Optional[str] = None 