"""
Message router for Kaiwhakarite Rawa
System Developer: Merryh Dugenia Vecino
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..auth.dependencies import get_current_user
from ..models.users import User
from ..services.message_service import MessageService
from ..schemas.messages import (
    MessageCreate, MessageUpdate, MessageResponse, MessageThreadCreate,
    ThreadMessageCreate, BulkMessageCreate, MessageSearch, MessageStats,
    MessageTemplateCreate, MessageTemplateUpdate, MessageTemplateResponse
)
from ..models.messages import MessageType, MessagePriority, MessageStatus, MessageTemplate
from ..models.inventory import InventoryItem
from ..models.calendar import CalendarEvent

router = APIRouter()


@router.post("/", response_model=MessageResponse)
def create_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new message"""
    message_service = MessageService(db)
    
    # Set sender to current user
    message_data.sender_id = current_user.id
    
    # Validate recipient exists
    recipient = db.query(User).filter(User.id == message_data.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    message = message_service.create_message(message_data, current_user.id)
    
    # Add sender and recipient names to response
    response_data = MessageResponse.from_orm(message)
    response_data.sender_name = current_user.full_name
    response_data.recipient_name = recipient.full_name
    
    return response_data


@router.post("/bulk", response_model=List[MessageResponse])
def create_bulk_messages(
    bulk_data: BulkMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send messages to multiple recipients"""
    message_service = MessageService(db)
    
    # Validate all recipients exist
    for recipient_id in bulk_data.recipient_ids:
        recipient = db.query(User).filter(User.id == recipient_id).first()
        if not recipient:
            raise HTTPException(status_code=404, detail=f"Recipient {recipient_id} not found")
    
    messages = message_service.create_bulk_messages(bulk_data, current_user.id)
    
    # Add sender and recipient names to responses
    response_data = []
    for message in messages:
        response = MessageResponse.from_orm(message)
        response.sender_name = current_user.full_name
        response.recipient_name = message.recipient.full_name
        response_data.append(response)
    
    return response_data


@router.get("/", response_model=List[MessageResponse])
def get_messages(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for current user (sent and received)"""
    message_service = MessageService(db)
    messages = message_service.get_user_messages(current_user.id, limit, offset)
    
    response_data = []
    for message in messages:
        response = MessageResponse.from_orm(message)
        response.sender_name = message.sender.full_name if message.sender else None
        response.recipient_name = message.recipient.full_name if message.recipient else None
        response_data.append(response)
    
    return response_data


@router.get("/inbox", response_model=List[MessageResponse])
def get_inbox_messages(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get received messages for current user"""
    message_service = MessageService(db)
    messages = message_service.get_inbox_messages(current_user.id, limit, offset)
    
    response_data = []
    for message in messages:
        response = MessageResponse.from_orm(message)
        response.sender_name = message.sender.full_name if message.sender else None
        response.recipient_name = message.recipient.full_name if message.recipient else None
        response_data.append(response)
    
    return response_data


@router.get("/sent", response_model=List[MessageResponse])
def get_sent_messages(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sent messages for current user"""
    message_service = MessageService(db)
    messages = message_service.get_sent_messages(current_user.id, limit, offset)
    
    response_data = []
    for message in messages:
        response = MessageResponse.from_orm(message)
        response.sender_name = message.sender.full_name if message.sender else None
        response.recipient_name = message.recipient.full_name if message.recipient else None
        response_data.append(response)
    
    return response_data


@router.get("/unread", response_model=List[MessageResponse])
def get_unread_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unread messages for current user"""
    message_service = MessageService(db)
    messages = message_service.get_unread_messages(current_user.id)
    
    response_data = []
    for message in messages:
        response = MessageResponse.from_orm(message)
        response.sender_name = message.sender.full_name if message.sender else None
        response.recipient_name = message.recipient.full_name if message.recipient else None
        response_data.append(response)
    
    return response_data


@router.put("/{message_id}/read")
def mark_message_as_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a message as read"""
    message_service = MessageService(db)
    success = message_service.mark_as_read(message_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return {"message": "Message marked as read"}


@router.put("/read-all")
def mark_all_messages_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all messages as read for current user"""
    message_service = MessageService(db)
    count = message_service.mark_all_as_read(current_user.id)
    
    return {"message": f"{count} messages marked as read"}


@router.put("/{message_id}/archive")
def archive_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive a message"""
    message_service = MessageService(db)
    success = message_service.archive_message(message_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return {"message": "Message archived"}


@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a message (soft delete)"""
    message_service = MessageService(db)
    success = message_service.delete_message(message_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return {"message": "Message deleted"}


@router.post("/search", response_model=List[MessageResponse])
def search_messages(
    search_data: MessageSearch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search messages with filters"""
    message_service = MessageService(db)
    messages = message_service.search_messages(search_data, current_user.id)
    
    response_data = []
    for message in messages:
        response = MessageResponse.from_orm(message)
        response.sender_name = message.sender.full_name if message.sender else None
        response.recipient_name = message.recipient.full_name if message.recipient else None
        response_data.append(response)
    
    return response_data


@router.get("/stats", response_model=MessageStats)
def get_message_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get message statistics for current user"""
    message_service = MessageService(db)
    return message_service.get_message_stats(current_user.id)


# Thread endpoints
@router.post("/threads", response_model=MessageResponse)
def create_message_thread(
    thread_data: MessageThreadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new message thread"""
    message_service = MessageService(db)
    
    # Set creator to current user
    thread_data.created_by_id = current_user.id
    
    # Validate all participants exist
    for participant_id in thread_data.participant_ids:
        participant = db.query(User).filter(User.id == participant_id).first()
        if not participant:
            raise HTTPException(status_code=404, detail=f"Participant {participant_id} not found")
    
    thread = message_service.create_message_thread(thread_data, current_user.id)
    
    response_data = MessageResponse.from_orm(thread)
    response_data.created_by_name = current_user.full_name
    response_data.participant_count = len(thread_data.participant_ids)
    
    return response_data


@router.get("/threads", response_model=List[MessageResponse])
def get_user_threads(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get message threads for current user"""
    message_service = MessageService(db)
    threads = message_service.get_user_threads(current_user.id, limit, offset)
    
    response_data = []
    for thread in threads:
        response = MessageResponse.from_orm(thread)
        response.created_by_name = thread.created_by.full_name if thread.created_by else None
        response.participant_count = len(thread.participants)
        response_data.append(response)
    
    return response_data


@router.post("/threads/{thread_id}/messages", response_model=MessageResponse)
def add_thread_message(
    thread_id: int,
    message_data: ThreadMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a message to a thread"""
    message_service = MessageService(db)
    
    # Set thread ID and sender
    message_data.thread_id = thread_id
    message_data.sender_id = current_user.id
    
    try:
        message = message_service.add_thread_message(message_data, current_user.id)
        
        response_data = MessageResponse.from_orm(message)
        response_data.sender_name = current_user.full_name
        
        return response_data
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/threads/{thread_id}/messages", response_model=List[MessageResponse])
def get_thread_messages(
    thread_id: int,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages in a thread"""
    message_service = MessageService(db)
    
    try:
        messages = message_service.get_thread_messages(thread_id, current_user.id, limit, offset)
        
        response_data = []
        for message in messages:
            response = MessageResponse.from_orm(message)
            response.sender_name = message.sender.full_name if message.sender else None
            response_data.append(response)
        
        return response_data
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


# Template endpoints (admin only)
@router.post("/templates", response_model=MessageTemplateResponse)
def create_message_template(
    template_data: MessageTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new message template (admin only)"""
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if template name already exists
    existing = db.query(MessageTemplate).filter(MessageTemplate.name == template_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Template name already exists")
    
    template = MessageTemplate(**template_data.dict())
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return MessageTemplateResponse.from_orm(template)


@router.get("/templates", response_model=List[MessageTemplateResponse])
def get_message_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all message templates"""
    templates = db.query(MessageTemplate).filter(MessageTemplate.is_active == True).all()
    return [MessageTemplateResponse.from_orm(template) for template in templates]


# Special message endpoints
@router.post("/inventory/{item_id}")
def send_inventory_message(
    item_id: int,
    subject: str,
    content: str,
    recipient_id: int,
    cultural_context: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message related to an inventory item"""
    message_service = MessageService(db)
    
    # Validate item exists
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Validate recipient exists
    recipient = db.query(User).filter(User.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    message = message_service.create_inventory_message(
        item, current_user.id, recipient_id, subject, content, cultural_context
    )
    
    return {"message": "Inventory message sent", "message_id": message.id}


@router.post("/cultural-event/{event_id}")
def send_cultural_event_message(
    event_id: int,
    subject: str,
    content: str,
    recipient_id: int,
    cultural_context: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message related to a cultural event"""
    message_service = MessageService(db)
    
    # Validate event exists
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Cultural event not found")
    
    # Validate recipient exists
    recipient = db.query(User).filter(User.id == recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    message = message_service.create_cultural_event_message(
        event, current_user.id, recipient_id, subject, content, cultural_context
    )
    
    return {"message": "Cultural event message sent", "message_id": message.id} 