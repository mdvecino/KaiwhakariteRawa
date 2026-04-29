from sqlalchemy import Column, String, Integer, Text, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from ..models.base import BaseModel


class NotificationType(str, enum.Enum):
    LOW_STOCK = "low_stock"
    CULTURAL_EVENT = "cultural_event"
    SYSTEM_ALERT = "system_alert"
    MAINTENANCE = "maintenance"
    SECURITY = "security"
    GENERAL = "general"


class NotificationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class Notification(BaseModel):
    """Notification model for system alerts and messages"""
    __tablename__ = "notifications"
    
    # Basic notification info
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    
    # Recipient and sender
    recipient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Delivery channels
    email_sent = Column(Boolean, default=False)
    sms_sent = Column(Boolean, default=False)
    push_sent = Column(Boolean, default=False)
    in_app_sent = Column(Boolean, default=False)
    
    # Timing
    scheduled_for = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Additional data
    notification_data = Column(Text, nullable=True)  # JSON string for additional data
    related_item_id = Column(Integer, nullable=True)  # Related inventory item
    related_event_id = Column(Integer, nullable=True)  # Related calendar event
    
    # Cultural considerations
    cultural_context = Column(Text, nullable=True)
    iwi_connection = Column(String(100), nullable=True)
    
    # Relationships
    recipient = relationship("User", foreign_keys=[recipient_id])
    sender = relationship("User", foreign_keys=[sender_id])


class NotificationTemplate(BaseModel):
    """Template for common notifications"""
    __tablename__ = "notification_templates"
    
    name = Column(String(100), nullable=False, unique=True)
    title_template = Column(String(200), nullable=False)
    message_template = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    
    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    
    # Cultural considerations
    cultural_context = Column(Text, nullable=True)
    bilingual_support = Column(Boolean, default=False)
    maori_title_template = Column(String(200), nullable=True)
    maori_message_template = Column(Text, nullable=True)
    
    # Template variables (JSON string)
    variables = Column(Text, nullable=True)  # JSON array of variable names
    is_active = Column(Boolean, default=True) 