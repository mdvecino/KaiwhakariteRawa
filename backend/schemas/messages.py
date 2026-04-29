"""
Message schemas for Kaiwhakarite Rawa
System Developer: Merryh Dugenia Vecino
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ..models.messages import MessageType, MessagePriority, MessageStatus


class MessageBase(BaseModel):
    """Base message schema"""
    subject: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.GENERAL
    priority: MessagePriority = MessagePriority.MEDIUM
    cultural_context: Optional[str] = None
    iwi_connection: Optional[str] = None
    cultural_protocol: Optional[str] = None
    requires_response: bool = False
    response_deadline: Optional[datetime] = None
    related_item_id: Optional[int] = None
    related_event_id: Optional[int] = None


class MessageCreate(MessageBase):
    """Schema for creating a new message"""
    recipient_id: int
    sender_id: Optional[int] = None  # Will be set from current user


class MessageUpdate(BaseModel):
    """Schema for updating a message"""
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    priority: Optional[MessagePriority] = None
    cultural_context: Optional[str] = None
    iwi_connection: Optional[str] = None
    requires_response: Optional[bool] = None
    response_deadline: Optional[datetime] = None


class MessageResponse(MessageBase):
    """Schema for message response"""
    id: int
    sender_id: int
    recipient_id: int
    status: MessageStatus
    sent_at: datetime
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    is_encrypted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    # Sender and recipient info
    sender_name: Optional[str] = None
    recipient_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class MessageThreadBase(BaseModel):
    """Base message thread schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    thread_type: MessageType = MessageType.GENERAL
    is_private: bool = True
    cultural_context: Optional[str] = None
    iwi_connection: Optional[str] = None


class MessageThreadCreate(MessageThreadBase):
    """Schema for creating a new message thread"""
    participant_ids: List[int] = Field(..., min_items=1)
    created_by_id: Optional[int] = None  # Will be set from current user


class MessageThreadUpdate(BaseModel):
    """Schema for updating a message thread"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    is_archived: Optional[bool] = None
    is_private: Optional[bool] = None
    cultural_context: Optional[str] = None
    iwi_connection: Optional[str] = None


class MessageThreadResponse(MessageThreadBase):
    """Schema for message thread response"""
    id: int
    created_by_id: int
    is_archived: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    # Participant info
    participant_count: int
    created_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ThreadMessageBase(BaseModel):
    """Base thread message schema"""
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.GENERAL
    cultural_context: Optional[str] = None
    reply_to_id: Optional[int] = None


class ThreadMessageCreate(ThreadMessageBase):
    """Schema for creating a new thread message"""
    thread_id: int
    sender_id: Optional[int] = None  # Will be set from current user


class ThreadMessageUpdate(BaseModel):
    """Schema for updating a thread message"""
    content: Optional[str] = Field(None, min_length=1)
    cultural_context: Optional[str] = None


class ThreadMessageResponse(ThreadMessageBase):
    """Schema for thread message response"""
    id: int
    thread_id: int
    sender_id: int
    is_edited: bool
    edited_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    
    # Sender info
    sender_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class MessageTemplateBase(BaseModel):
    """Base message template schema"""
    name: str = Field(..., min_length=1, max_length=100)
    subject_template: str = Field(..., min_length=1, max_length=200)
    content_template: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.GENERAL
    priority: MessagePriority = MessagePriority.MEDIUM
    cultural_context: Optional[str] = None
    bilingual_support: bool = False
    maori_subject_template: Optional[str] = None
    maori_content_template: Optional[str] = None
    variables: Optional[str] = None  # JSON string


class MessageTemplateCreate(MessageTemplateBase):
    """Schema for creating a new message template"""
    pass


class MessageTemplateUpdate(BaseModel):
    """Schema for updating a message template"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    subject_template: Optional[str] = Field(None, min_length=1, max_length=200)
    content_template: Optional[str] = Field(None, min_length=1)
    message_type: Optional[MessageType] = None
    priority: Optional[MessagePriority] = None
    is_active: Optional[bool] = None
    cultural_context: Optional[str] = None
    bilingual_support: Optional[bool] = None
    maori_subject_template: Optional[str] = None
    maori_content_template: Optional[str] = None
    variables: Optional[str] = None


class MessageTemplateResponse(MessageTemplateBase):
    """Schema for message template response"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MessageStats(BaseModel):
    """Message statistics"""
    total_messages: int
    unread_messages: int
    sent_messages: int
    received_messages: int
    messages_by_type: Dict[str, int]
    messages_by_priority: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


class BulkMessageCreate(BaseModel):
    """Schema for sending bulk messages"""
    subject: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    recipient_ids: List[int] = Field(..., min_items=1)
    message_type: MessageType = MessageType.GENERAL
    priority: MessagePriority = MessagePriority.MEDIUM
    cultural_context: Optional[str] = None
    iwi_connection: Optional[str] = None
    requires_response: bool = False
    response_deadline: Optional[datetime] = None


class MessageSearch(BaseModel):
    """Schema for message search"""
    query: Optional[str] = None
    message_type: Optional[MessageType] = None
    priority: Optional[MessagePriority] = None
    status: Optional[MessageStatus] = None
    sender_id: Optional[int] = None
    recipient_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    cultural_context: Optional[str] = None
    iwi_connection: Optional[str] = None
    limit: int = 50
    offset: int = 0 