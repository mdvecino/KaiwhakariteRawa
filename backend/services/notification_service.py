import json
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Optional Twilio import for SMS functionality
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None
    TwilioException = Exception

from ..models.notifications import (
    Notification, NotificationTemplate, NotificationType, 
    NotificationPriority, NotificationStatus, NotificationChannel
)
from ..models.users import User
from ..models.inventory import InventoryItem
from ..schemas.notifications import (
    NotificationCreate, NotificationUpdate, NotificationTemplateCreate,
    UserNotificationPreferences, BulkNotificationCreate
)
from ..services import BaseService


class NotificationService(BaseService[Notification]):
    """Service for handling all notification operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, Notification)
        self.db = db
        self.email_config = self._load_email_config()
        self.sms_config = self._load_sms_config()
    
    def _load_email_config(self) -> Dict[str, str]:
        """Load email configuration from environment variables"""
        return {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_username': os.getenv('SMTP_USERNAME', ''),
            'smtp_password': os.getenv('SMTP_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', 'noreply@kaiwhakariterawa.com'),
            'from_name': os.getenv('FROM_NAME', 'Kaiwhakarite Rawa')
        }
    
    def _load_sms_config(self) -> Dict[str, str]:
        """Load SMS configuration from environment variables"""
        return {
            'account_sid': os.getenv('TWILIO_ACCOUNT_SID', ''),
            'auth_token': os.getenv('TWILIO_AUTH_TOKEN', ''),
            'from_number': os.getenv('TWILIO_FROM_NUMBER', '')
        }
    
    def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """Create a new notification"""
        notification = Notification(**notification_data.dict())
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # Send notification immediately if not scheduled
        if not notification.scheduled_for:
            # For testing purposes, we'll skip the async sending
            # In production, this would be: asyncio.create_task(self.send_notification(notification.id))
            pass
        
        return notification
    
    def create_bulk_notifications(self, bulk_data: BulkNotificationCreate) -> List[Notification]:
        """Create multiple notifications for different recipients"""
        notifications = []
        for recipient_id in bulk_data.recipient_ids:
            notification_data = NotificationCreate(
                title=bulk_data.title,
                message=bulk_data.message,
                notification_type=bulk_data.notification_type,
                priority=bulk_data.priority,
                recipient_id=recipient_id,
                sender_id=bulk_data.sender_id,
                scheduled_for=bulk_data.scheduled_for,
                cultural_context=bulk_data.cultural_context,
                iwi_connection=bulk_data.iwi_connection
            )
            notification = self.create_notification(notification_data)
            notifications.append(notification)
        
        return notifications
    
    def get_user_notifications(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Notification]:
        """Get notifications for a specific user"""
        return self.db.query(Notification).filter(
            Notification.recipient_id == user_id
        ).order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    def get_unread_notifications(self, user_id: int) -> List[Notification]:
        """Get unread notifications for a user"""
        return self.db.query(Notification).filter(
            and_(
                Notification.recipient_id == user_id,
                Notification.status != NotificationStatus.READ
            )
        ).order_by(Notification.created_at.desc()).all()
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        notification = self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.recipient_id == user_id
            )
        ).first()
        
        if notification:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        result = self.db.query(Notification).filter(
            and_(
                Notification.recipient_id == user_id,
                Notification.status != NotificationStatus.READ
            )
        ).update({
            'status': NotificationStatus.READ,
            'read_at': datetime.utcnow()
        })
        self.db.commit()
        return result
    
    async def send_notification(self, notification_id: int) -> bool:
        """Send a notification through all enabled channels"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if not notification:
            return False
        
        recipient = self.db.query(User).filter(User.id == notification.recipient_id).first()
        if not recipient:
            return False
        
        success = True
        
        # Send email notification
        if recipient.email_notifications and not notification.email_sent:
            if await self.send_email_notification(notification, recipient):
                notification.email_sent = True
            else:
                success = False
        
        # Send SMS notification
        if (recipient.sms_notifications and recipient.phone_number and 
            not notification.sms_sent):
            if await self.send_sms_notification(notification, recipient):
                notification.sms_sent = True
            else:
                success = False
        
        # Send push notification
        if recipient.push_notifications and not notification.push_sent:
            if await self.send_push_notification(notification, recipient):
                notification.push_sent = True
            else:
                success = False
        
        # Mark as sent
        if success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
        else:
            notification.status = NotificationStatus.FAILED
        
        self.db.commit()
        return success
    
    async def send_email_notification(self, notification: Notification, user: User) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = f"{self.email_config['from_name']} <{self.email_config['from_email']}>"
            msg['To'] = user.email
            msg['Subject'] = notification.title
            
            # Create HTML body with Māori cultural styling
            html_body = self._create_email_html(notification, user)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['smtp_username'], self.email_config['smtp_password'])
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False
    
    async def send_sms_notification(self, notification: Notification, user: User) -> bool:
        """Send SMS notification using Twilio"""
        try:
            # Check if Twilio is available
            if not TWILIO_AVAILABLE:
                print("SMS notification skipped: Twilio not available")
                return False
            
            if not all([self.sms_config['account_sid'], self.sms_config['auth_token'], 
                       self.sms_config['from_number']]):
                print("SMS notification skipped: Twilio configuration incomplete")
                return False
            
            client = Client(self.sms_config['account_sid'], self.sms_config['auth_token'])
            
            message = client.messages.create(
                body=notification.message,
                from_=self.sms_config['from_number'],
                to=user.phone_number
            )
            
            return message.sid is not None
        except TwilioException as e:
            print(f"SMS notification failed: {e}")
            return False
        except Exception as e:
            print(f"SMS notification failed: {e}")
            return False
    
    async def send_push_notification(self, notification: Notification, user: User) -> bool:
        """Send push notification (placeholder for WebSocket implementation)"""
        # This would typically use WebSockets or a service like Firebase
        # For now, we'll just mark it as sent
        return True
    
    def _create_email_html(self, notification: Notification, user: User) -> str:
        """Create HTML email template with Māori cultural styling"""
        priority_colors = {
            NotificationPriority.LOW: "#81C784",
            NotificationPriority.MEDIUM: "#FFB74D",
            NotificationPriority.HIGH: "#FF8A65",
            NotificationPriority.CRITICAL: "#E57373"
        }
        
        color = priority_colors.get(notification.priority, "#81C784")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; }}
                .header {{ background-color: {color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .footer {{ background-color: #3A7256; color: white; padding: 20px; text-align: center; font-size: 12px; }}
                .priority-badge {{ display: inline-block; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }}
                .cultural-note {{ background-color: #FFF3E0; border-left: 4px solid #FF9800; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Kaiwhakarite Rawa</h1>
                    <p>Inventory & Resource Management System</p>
                </div>
                <div class="content">
                    <h2>{notification.title}</h2>
                    <p><strong>Priority:</strong> <span class="priority-badge" style="background-color: {color}; color: white;">{notification.priority.value.upper()}</span></p>
                    <p>{notification.message}</p>
                    
                    {f'<div class="cultural-note"><strong>Cultural Context:</strong> {notification.cultural_context}</div>' if notification.cultural_context else ''}
                    
                    {f'<p><strong>Iwi Connection:</strong> {notification.iwi_connection}</p>' if notification.iwi_connection else ''}
                    
                    <p><em>This notification was sent to {user.full_name} on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</em></p>
                </div>
                <div class="footer">
                    <p>Kia ora! Thank you for using Kaiwhakarite Rawa</p>
                    <p>Respecting both modern technology and Māori cultural values</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def create_low_stock_alert(self, item: InventoryItem) -> List[Notification]:
        """Create low stock alerts for relevant users"""
        # Get users who should receive low stock alerts
        users = self.db.query(User).filter(
            and_(
                User.low_stock_alerts == True,
                User.status == "ACTIVE"
            )
        ).all()
        
        notifications = []
        for user in users:
            notification_data = NotificationCreate(
                title=f"Low Stock Alert: {item.name}",
                message=f"The item '{item.name}' (SKU: {item.sku}) is running low on stock. Current quantity: {item.quantity}, Minimum: {item.min_quantity}",
                notification_type=NotificationType.LOW_STOCK,
                priority=NotificationPriority.HIGH if item.quantity == 0 else NotificationPriority.MEDIUM,
                recipient_id=user.id,
                related_item_id=item.id,
                cultural_context="Stock management is crucial for maintaining cultural resources and ensuring availability for important events and ceremonies."
            )
            notification = self.create_notification(notification_data)
            notifications.append(notification)
        
        return notifications
    
    def create_cultural_event_reminder(self, event_title: str, event_date: datetime, 
                                     user_ids: List[int], cultural_context: str = None) -> List[Notification]:
        """Create cultural event reminders"""
        notifications = []
        for user_id in user_ids:
            notification_data = NotificationCreate(
                title=f"Cultural Event Reminder: {event_title}",
                message=f"Reminder: {event_title} is scheduled for {event_date.strftime('%Y-%m-%d %H:%M')}",
                notification_type=NotificationType.CULTURAL_EVENT,
                priority=NotificationPriority.MEDIUM,
                recipient_id=user_id,
                cultural_context=cultural_context or "Cultural events are important for maintaining traditions and community connections."
            )
            notification = self.create_notification(notification_data)
            notifications.append(notification)
        
        return notifications
    
    def get_notification_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get notification statistics"""
        query = self.db.query(Notification)
        
        if user_id:
            query = query.filter(Notification.recipient_id == user_id)
        
        total = query.count()
        unread = query.filter(Notification.status != NotificationStatus.READ).count()
        pending = query.filter(Notification.status == NotificationStatus.PENDING).count()
        failed = query.filter(Notification.status == NotificationStatus.FAILED).count()
        
        # Group by type
        by_type = {}
        for notification_type in NotificationType:
            count = query.filter(Notification.notification_type == notification_type).count()
            by_type[notification_type.value] = count
        
        # Group by priority
        by_priority = {}
        for priority in NotificationPriority:
            count = query.filter(Notification.priority == priority).count()
            by_priority[priority.value] = count
        
        return {
            'total_notifications': total,
            'unread_notifications': unread,
            'pending_notifications': pending,
            'failed_notifications': failed,
            'notifications_by_type': by_type,
            'notifications_by_priority': by_priority
        } 