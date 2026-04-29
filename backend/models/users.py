from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
import enum
from .base import BaseModel


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    USER = "USER"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class User(BaseModel):
    """User model for authentication and role management"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    profile_image = Column(String(255), nullable=True)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    
    # Notification Preferences
    phone_number = Column(String(20), nullable=True)
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    low_stock_alerts = Column(Boolean, default=True)
    cultural_event_alerts = Column(Boolean, default=True)
    system_alerts = Column(Boolean, default=True)
    notification_frequency = Column(String(20), default="immediate")  # immediate, daily, weekly
    
    # Relationships
    inventory_items = relationship("InventoryItem", 
                                back_populates="created_by")
    suppliers = relationship("Supplier", back_populates="created_by")
    calendar_events = relationship("CalendarEvent", 
                                back_populates="created_by")
    supplier_returns_created = relationship("SupplierReturn", 
                                          foreign_keys="SupplierReturn.created_by_id",
                                          back_populates="created_by")
    supplier_returns_approved = relationship("SupplierReturn", 
                                           foreign_keys="SupplierReturn.approved_by_id",
                                           back_populates="approved_by")
    
    # Message relationships
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.recipient_id", back_populates="recipient")
    created_threads = relationship("MessageThread", back_populates="created_by")
    thread_participations = relationship("MessageThreadParticipant", back_populates="user")
    thread_messages = relationship("ThreadMessage", back_populates="sender") 