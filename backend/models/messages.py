"""
Message models for Kaiwhakarite Rawa
System Developer: Merryh Dugenia Vecino
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from ..models.base import BaseModel


class MessageType(PyEnum):
    """Types of messages"""
    GENERAL = "general"
    INVENTORY = "inventory"
    CULTURAL = "cultural"
    EVENT = "event"
    URGENT = "urgent"
    SYSTEM = "system"


class MessagePriority(PyEnum):
    """Message priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MessageStatus(PyEnum):
    """Message status"""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    ARCHIVED = "archived"


class Message(BaseModel):
    """Message model for user-to-user communication"""
    __tablename__ = "messages"
    
    # Message content
    subject = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.GENERAL)
    priority = Column(Enum(MessagePriority), default=MessagePriority.MEDIUM)
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT)
    
    # Sender and recipient
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Message metadata
    is_encrypted = Column(Boolean, default=False)
    requires_response = Column(Boolean, default=False)
    response_deadline = Column(DateTime, nullable=True)
    
    # Cultural context
    cultural_context = Column(Text, nullable=True)
    iwi_connection = Column(String(100), nullable=True)
    cultural_protocol = Column(String(100), nullable=True)
    
    # Related items
    related_item_id = Column(Integer, ForeignKey("inventory_items.id", ondelete="SET NULL"), nullable=True)
    related_event_id = Column(Integer, ForeignKey("calendar_events.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    sent_at = Column(DateTime, default=func.now())
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages")
    related_item = relationship("InventoryItem", back_populates="messages")
    related_event = relationship("CalendarEvent", back_populates="messages")


class MessageThread(BaseModel):
    """Message thread for organizing conversations"""
    __tablename__ = "message_threads"
    
    # Thread information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    thread_type = Column(Enum(MessageType), default=MessageType.GENERAL)
    
    # Participants
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Thread metadata
    is_archived = Column(Boolean, default=False)
    is_private = Column(Boolean, default=True)
    
    # Cultural context
    cultural_context = Column(Text, nullable=True)
    iwi_connection = Column(String(100), nullable=True)
    
    # Relationships
    created_by = relationship("User", back_populates="created_threads")
    participants = relationship("MessageThreadParticipant", back_populates="thread")
    messages = relationship("ThreadMessage", back_populates="thread", order_by="ThreadMessage.created_at")


class MessageThreadParticipant(BaseModel):
    """Participants in message threads"""
    __tablename__ = "message_thread_participants"
    
    thread_id = Column(Integer, ForeignKey("message_threads.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Participant role
    is_admin = Column(Boolean, default=False)
    can_invite = Column(Boolean, default=False)
    
    # Timestamps
    joined_at = Column(DateTime, default=func.now())
    last_read_at = Column(DateTime, nullable=True)
    
    # Relationships
    thread = relationship("MessageThread", back_populates="participants")
    user = relationship("User", back_populates="thread_participations")


class ThreadMessage(BaseModel):
    """Messages within a thread"""
    __tablename__ = "thread_messages"
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.GENERAL)
    
    # Thread and sender
    thread_id = Column(Integer, ForeignKey("message_threads.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Message metadata
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime, nullable=True)
    reply_to_id = Column(Integer, ForeignKey("thread_messages.id", ondelete="SET NULL"), nullable=True)
    
    # Cultural context
    cultural_context = Column(Text, nullable=True)
    
    # Relationships
    thread = relationship("MessageThread", back_populates="messages")
    sender = relationship("User", back_populates="thread_messages")
    reply_to = relationship("ThreadMessage", remote_side="ThreadMessage.id")


class MessageTemplate(BaseModel):
    """Templates for common messages"""
    __tablename__ = "message_templates"
    
    # Template information
    name = Column(String(100), nullable=False, unique=True)
    subject_template = Column(String(200), nullable=False)
    content_template = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.GENERAL)
    priority = Column(Enum(MessagePriority), default=MessagePriority.MEDIUM)
    
    # Template metadata
    is_active = Column(Boolean, default=True)
    variables = Column(Text, nullable=True)  # JSON string of available variables
    
    # Cultural context
    cultural_context = Column(Text, nullable=True)
    bilingual_support = Column(Boolean, default=False)
    maori_subject_template = Column(String(200), nullable=True)
    maori_content_template = Column(Text, nullable=True) 