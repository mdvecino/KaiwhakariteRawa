"""
Message service for Kaiwhakarite Rawa
System Developer: Merryh Dugenia Vecino
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from ..models.messages import (
    Message, MessageThread, MessageThreadParticipant, ThreadMessage, 
    MessageTemplate, MessageType, MessagePriority, MessageStatus
)
from ..models.users import User
from ..models.inventory import InventoryItem
from ..models.calendar import CalendarEvent
from ..schemas.messages import (
    MessageCreate, MessageUpdate, MessageThreadCreate, ThreadMessageCreate,
    BulkMessageCreate, MessageSearch, MessageStats
)
from ..services.notification_service import NotificationService
from ..schemas.notifications import NotificationCreate
from ..models.notifications import NotificationType, NotificationPriority
import logging
from ..services import BaseService


class MessageService(BaseService[Message]):
    """Service for handling all messaging operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Message)
        self.db = db
        try:
            self.notification_service = NotificationService(db)
        except Exception as e:
            logging.warning(f"Could not initialize notification service: {e}")
            self.notification_service = None
    
    def create_message(self, message_data: MessageCreate, sender_id: int) -> Message:
        """Create a new message"""
        message = Message(**message_data.dict(), sender_id=sender_id)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        if self.notification_service:
            try:
                self._create_message_notification(message)
            except Exception as e:
                logging.warning(f"Could not create notification: {e}")
        
        return message
    
    def create_bulk_messages(self, bulk_data: BulkMessageCreate, sender_id: int) -> List[Message]:
        """Create multiple messages for different recipients"""
        messages = []
        for recipient_id in bulk_data.recipient_ids:
            message_data = MessageCreate(
                subject=bulk_data.subject,
                content=bulk_data.content,
                message_type=bulk_data.message_type,
                priority=bulk_data.priority,
                recipient_id=recipient_id,
                cultural_context=bulk_data.cultural_context,
                iwi_connection=bulk_data.iwi_connection,
                requires_response=bulk_data.requires_response,
                response_deadline=bulk_data.response_deadline
            )
            message = self.create_message(message_data, sender_id)
            messages.append(message)
        
        return messages
    
    def get_user_messages(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        """Get messages for a specific user (both sent and received)"""
        return self.db.query(Message).filter(
            or_(
                Message.sender_id == user_id,
                Message.recipient_id == user_id
            )
        ).order_by(desc(Message.sent_at)).offset(offset).limit(limit).all()
    
    def get_inbox_messages(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        """Get received messages for a user"""
        return self.db.query(Message).filter(
            and_(
                Message.recipient_id == user_id,
                Message.status != MessageStatus.ARCHIVED
            )
        ).order_by(desc(Message.sent_at)).offset(offset).limit(limit).all()
    
    def get_sent_messages(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        """Get sent messages for a user"""
        return self.db.query(Message).filter(
            Message.sender_id == user_id
        ).order_by(desc(Message.sent_at)).offset(offset).limit(limit).all()
    
    def get_unread_messages(self, user_id: int) -> List[Message]:
        """Get unread messages for a user"""
        return self.db.query(Message).filter(
            and_(
                Message.recipient_id == user_id,
                Message.status != MessageStatus.READ,
                Message.status != MessageStatus.ARCHIVED
            )
        ).order_by(desc(Message.sent_at)).all()
    
    def mark_as_read(self, message_id: int, user_id: int) -> bool:
        """Mark a message as read"""
        message = self.db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.recipient_id == user_id
            )
        ).first()
        
        if message:
            message.status = MessageStatus.READ
            message.read_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all messages as read for a user"""
        result = self.db.query(Message).filter(
            and_(
                Message.recipient_id == user_id,
                Message.status != MessageStatus.READ,
                Message.status != MessageStatus.ARCHIVED
            )
        ).update({
            'status': MessageStatus.READ,
            'read_at': datetime.utcnow()
        })
        self.db.commit()
        return result
    
    def archive_message(self, message_id: int, user_id: int) -> bool:
        """Archive a message"""
        message = self.db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.recipient_id == user_id
            )
        ).first()
        
        if message:
            message.status = MessageStatus.ARCHIVED
            self.db.commit()
            return True
        return False
    
    def delete_message(self, message_id: int, user_id: int) -> bool:
        """Delete a message (soft delete)"""
        message = self.db.query(Message).filter(
            and_(
                Message.id == message_id,
                or_(
                    Message.sender_id == user_id,
                    Message.recipient_id == user_id
                )
            )
        ).first()
        
        if message:
            message.is_active = False
            self.db.commit()
            return True
        return False
    
    def search_messages(self, search_data: MessageSearch, user_id: int) -> List[Message]:
        """Search messages with filters"""
        query = self.db.query(Message).filter(
            or_(
                Message.sender_id == user_id,
                Message.recipient_id == user_id
            )
        )
        
        if search_data.query:
            query = query.filter(
                or_(
                    Message.subject.contains(search_data.query),
                    Message.content.contains(search_data.query)
                )
            )
        
        if search_data.message_type:
            query = query.filter(Message.message_type == search_data.message_type)
        
        if search_data.priority:
            query = query.filter(Message.priority == search_data.priority)
        
        if search_data.status:
            query = query.filter(Message.status == search_data.status)
        
        if search_data.sender_id:
            query = query.filter(Message.sender_id == search_data.sender_id)
        
        if search_data.recipient_id:
            query = query.filter(Message.recipient_id == search_data.recipient_id)
        
        if search_data.date_from:
            query = query.filter(Message.sent_at >= search_data.date_from)
        
        if search_data.date_to:
            query = query.filter(Message.sent_at <= search_data.date_to)
        
        if search_data.cultural_context:
            query = query.filter(Message.cultural_context.contains(search_data.cultural_context))
        
        if search_data.iwi_connection:
            query = query.filter(Message.iwi_connection.contains(search_data.iwi_connection))
        
        return query.order_by(desc(Message.sent_at)).offset(search_data.offset).limit(search_data.limit).all()
    
    def get_message_stats(self, user_id: int) -> MessageStats:
        """Get message statistics for a user"""
        # Total messages
        total_messages = self.db.query(Message).filter(
            or_(
                Message.sender_id == user_id,
                Message.recipient_id == user_id
            )
        ).count()
        
        # Unread messages
        unread_messages = self.db.query(Message).filter(
            and_(
                Message.recipient_id == user_id,
                Message.status != MessageStatus.READ,
                Message.status != MessageStatus.ARCHIVED
            )
        ).count()
        
        # Sent messages
        sent_messages = self.db.query(Message).filter(
            Message.sender_id == user_id
        ).count()
        
        # Received messages
        received_messages = self.db.query(Message).filter(
            Message.recipient_id == user_id
        ).count()
        
        # Messages by type
        messages_by_type = {}
        for message_type in MessageType:
            count = self.db.query(Message).filter(
                and_(
                    Message.message_type == message_type,
                    or_(
                        Message.sender_id == user_id,
                        Message.recipient_id == user_id
                    )
                )
            ).count()
            messages_by_type[message_type.value] = count
        
        # Messages by priority
        messages_by_priority = {}
        for priority in MessagePriority:
            count = self.db.query(Message).filter(
                and_(
                    Message.priority == priority,
                    or_(
                        Message.sender_id == user_id,
                        Message.recipient_id == user_id
                    )
                )
            ).count()
            messages_by_priority[priority.value] = count
        
        # Recent activity
        recent_activity = self.db.query(Message).filter(
            or_(
                Message.sender_id == user_id,
                Message.recipient_id == user_id
            )
        ).order_by(desc(Message.sent_at)).limit(10).all()
        
        recent_activity_data = []
        for message in recent_activity:
            recent_activity_data.append({
                'id': message.id,
                'subject': message.subject,
                'type': message.message_type.value,
                'sent_at': message.sent_at,
                'sender_name': message.sender.full_name if message.sender else None,
                'recipient_name': message.recipient.full_name if message.recipient else None
            })
        
        return MessageStats(
            total_messages=total_messages,
            unread_messages=unread_messages,
            sent_messages=sent_messages,
            received_messages=received_messages,
            messages_by_type=messages_by_type,
            messages_by_priority=messages_by_priority,
            recent_activity=recent_activity_data
        )
    
    def create_message_thread(self, thread_data: MessageThreadCreate, created_by_id: int) -> MessageThread:
        """Create a new message thread"""
        thread = MessageThread(**thread_data.dict(), created_by_id=created_by_id)
        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)
        
        # Add participants
        for participant_id in thread_data.participant_ids:
            participant = MessageThreadParticipant(
                thread_id=thread.id,
                user_id=participant_id,
                is_admin=participant_id == created_by_id,
                can_invite=participant_id == created_by_id
            )
            self.db.add(participant)
        
        self.db.commit()
        return thread
    
    def add_thread_message(self, message_data: ThreadMessageCreate, sender_id: int) -> ThreadMessage:
        """Add a message to a thread"""
        # Check if user is participant
        participant = self.db.query(MessageThreadParticipant).filter(
            and_(
                MessageThreadParticipant.thread_id == message_data.thread_id,
                MessageThreadParticipant.user_id == sender_id
            )
        ).first()
        
        if not participant:
            raise ValueError("User is not a participant in this thread")
        
        message = ThreadMessage(**message_data.dict(), sender_id=sender_id)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        # Update last read timestamp for sender
        participant.last_read_at = datetime.utcnow()
        self.db.commit()
        
        # Create notifications for other participants
        self._create_thread_message_notifications(message)
        
        return message
    
    def get_user_threads(self, user_id: int, limit: int = 50, offset: int = 0) -> List[MessageThread]:
        """Get threads for a user"""
        return self.db.query(MessageThread).join(MessageThreadParticipant).filter(
            MessageThreadParticipant.user_id == user_id
        ).order_by(desc(MessageThread.updated_at)).offset(offset).limit(limit).all()
    
    def get_thread_messages(self, thread_id: int, user_id: int, limit: int = 100, offset: int = 0) -> List[ThreadMessage]:
        """Get messages in a thread"""
        # Check if user is participant
        participant = self.db.query(MessageThreadParticipant).filter(
            and_(
                MessageThreadParticipant.thread_id == thread_id,
                MessageThreadParticipant.user_id == user_id
            )
        ).first()
        
        if not participant:
            raise ValueError("User is not a participant in this thread")
        
        # Update last read timestamp
        participant.last_read_at = datetime.utcnow()
        self.db.commit()
        
        return self.db.query(ThreadMessage).filter(
            ThreadMessage.thread_id == thread_id
        ).order_by(ThreadMessage.created_at).offset(offset).limit(limit).all()
    
    def _create_message_notification(self, message: Message):
        """Create notification for new message"""
        # Get sender name safely
        sender = self.db.query(User).filter(User.id == message.sender_id).first()
        sender_name = sender.full_name if sender else "Unknown User"
        
        notification_data = NotificationCreate(
            title=f"New Message: {message.subject}",
            message=f"You have received a new message from {sender_name}",
            notification_type=NotificationType.GENERAL,
            priority=NotificationPriority.MEDIUM if message.priority == MessagePriority.MEDIUM else NotificationPriority.HIGH,
            recipient_id=message.recipient_id,
            cultural_context=message.cultural_context or "Communication is important for maintaining relationships and cultural connections.",
            iwi_connection=message.iwi_connection
        )
        
        self.notification_service.create_notification(notification_data)
    
    def _create_thread_message_notifications(self, message: ThreadMessage):
        """Create notifications for thread messages"""
        # Get sender name safely
        sender = self.db.query(User).filter(User.id == message.sender_id).first()
        sender_name = sender.full_name if sender else "Unknown User"
        
        # Get thread title safely
        thread = self.db.query(MessageThread).filter(MessageThread.id == message.thread_id).first()
        thread_title = thread.title if thread else "Unknown Thread"
        
        # Get other participants
        participants = self.db.query(MessageThreadParticipant).filter(
            and_(
                MessageThreadParticipant.thread_id == message.thread_id,
                MessageThreadParticipant.user_id != message.sender_id
            )
        ).all()
        
        for participant in participants:
            notification_data = NotificationCreate(
                title=f"New Thread Message: {thread_title}",
                message=f"New message in thread '{thread_title}' from {sender_name}",
                notification_type=NotificationType.GENERAL,
                priority=NotificationPriority.MEDIUM,
                recipient_id=participant.user_id,
                cultural_context=message.cultural_context or "Group communication helps maintain community connections and cultural knowledge sharing."
            )
            
            self.notification_service.create_notification(notification_data)
    
    def create_inventory_message(self, item: InventoryItem, sender_id: int, recipient_id: int, 
                               subject: str, content: str, cultural_context: str = None) -> Message:
        """Create a message related to an inventory item"""
        message_data = MessageCreate(
            subject=subject,
            content=content,
            message_type=MessageType.INVENTORY,
            priority=MessagePriority.MEDIUM,
            recipient_id=recipient_id,
            related_item_id=item.id,
            cultural_context=cultural_context or f"Communication about taonga (treasured items) is important for proper care and cultural respect."
        )
        
        return self.create_message(message_data, sender_id)
    
    def create_cultural_event_message(self, event: CalendarEvent, sender_id: int, recipient_id: int,
                                    subject: str, content: str, cultural_context: str = None) -> Message:
        """Create a message related to a cultural event"""
        message_data = MessageCreate(
            subject=subject,
            content=content,
            message_type=MessageType.CULTURAL,
            priority=MessagePriority.MEDIUM,
            recipient_id=recipient_id,
            related_event_id=event.id,
            cultural_context=cultural_context or "Cultural events bring communities together and strengthen traditions."
        )
        
        return self.create_message(message_data, sender_id) 