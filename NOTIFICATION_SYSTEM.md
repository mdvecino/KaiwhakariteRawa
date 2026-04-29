# Notification System - Kaiwhakarite Rawa

A comprehensive notification system for the Kaiwhakarite Rawa inventory management platform with Māori cultural integration.

**System Developer: Merryh Dugenia Vecino**

## 🌟 Features

### **Multi-Channel Notifications**
- **Email Notifications**: HTML emails with Māori cultural styling
- **SMS Notifications**: Text messages via Twilio
- **Push Notifications**: Real-time browser notifications
- **In-App Notifications**: System notifications within the application

### **Cultural Integration**
- **Māori Cultural Context**: Cultural significance and protocols
- **Iwi Connections**: Tribal affiliations and relationships
- **Cultural Event Reminders**: Matariki, Maramataka, and other cultural events
- **Bilingual Support**: English and Te Reo Māori content

### **Smart Notifications**
- **Low Stock Alerts**: Automatic alerts when inventory is running low
- **Cultural Event Reminders**: Important cultural dates and ceremonies
- **System Alerts**: Maintenance, security, and general system notifications
- **Priority Levels**: Critical, High, Medium, Low priority notifications

### **User Preferences**
- **Channel Selection**: Choose which notification channels to use
- **Alert Types**: Enable/disable specific types of alerts
- **Frequency Control**: Immediate, daily, or weekly notification frequency
- **Phone Number**: Optional phone number for SMS notifications

## 🚀 Quick Start

### **1. Install Dependencies**

Add the notification dependencies to your backend:

```bash
cd backend
pip install fastapi-mail==1.4.1 twilio==8.10.0 websockets==12.0
```

### **2. Configure Environment Variables**

Create a `.env` file in the backend directory:

```env
# Email Notifications (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@kaiwhakariterawa.com
FROM_NAME=Kaiwhakarite Rawa

# SMS Notifications (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_FROM_NUMBER=+1234567890
```

### **3. Test the System**

Run the notification system test:

```bash
cd backend
python test_notifications.py
```

### **4. Access the Frontend**

The notification center is now available in the header of the application. Click the bell icon to:
- View all notifications
- Mark notifications as read
- Update notification preferences
- Send test notifications

## 📧 Email Configuration

### **Gmail Setup**
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Use the App Password in your SMTP_PASSWORD environment variable

### **Other Email Providers**
- **Outlook**: Use `smtp-mail.outlook.com` on port 587
- **Yahoo**: Use `smtp.mail.yahoo.com` on port 587
- **Custom SMTP**: Configure your own SMTP server

## 📱 SMS Configuration

### **Twilio Setup**
1. Create a Twilio account at [twilio.com](https://twilio.com)
2. Get your Account SID and Auth Token from the Twilio Console
3. Purchase a phone number for sending SMS
4. Add the credentials to your environment variables

### **Alternative SMS Providers**
The system can be easily extended to support other SMS providers like:
- AWS SNS
- MessageBird
- Vonage (formerly Nexmo)

## 🔧 API Endpoints

### **User Notifications**
- `GET /api/notifications/` - Get user notifications
- `GET /api/notifications/unread` - Get unread notifications
- `GET /api/notifications/stats` - Get notification statistics
- `POST /api/notifications/` - Create a notification
- `PUT /api/notifications/{id}/read` - Mark notification as read
- `PUT /api/notifications/read-all` - Mark all notifications as read

### **User Preferences**
- `GET /api/notifications/preferences` - Get user preferences
- `PUT /api/notifications/preferences` - Update user preferences

### **Admin Endpoints**
- `GET /api/notifications/templates` - Get notification templates
- `POST /api/notifications/templates` - Create notification template
- `PUT /api/notifications/templates/{id}` - Update notification template

### **Special Notifications**
- `POST /api/notifications/low-stock-alert/{item_id}` - Create low stock alert
- `POST /api/notifications/cultural-event-reminder` - Create cultural event reminder
- `POST /api/notifications/test` - Send test notification

## 📊 Notification Types

### **Low Stock Alerts**
```python
notification_data = NotificationCreate(
    title=f"Low Stock Alert: {item.name}",
    message=f"The item '{item.name}' is running low on stock.",
    notification_type=NotificationType.LOW_STOCK,
    priority=NotificationPriority.HIGH,
    recipient_id=user.id,
    related_item_id=item.id,
    cultural_context="Stock management is crucial for maintaining cultural resources."
)
```

### **Cultural Event Reminders**
```python
notification_data = NotificationCreate(
    title=f"Cultural Event Reminder: {event_title}",
    message=f"Reminder: {event_title} is scheduled for {event_date}",
    notification_type=NotificationType.CULTURAL_EVENT,
    priority=NotificationPriority.MEDIUM,
    recipient_id=user.id,
    cultural_context="Cultural events are important for maintaining traditions."
)
```

### **System Alerts**
```python
notification_data = NotificationCreate(
    title="System Maintenance",
    message="Scheduled maintenance will begin in 30 minutes.",
    notification_type=NotificationType.SYSTEM_ALERT,
    priority=NotificationPriority.MEDIUM,
    recipient_id=user.id
)
```

## 🎨 Email Templates

The system includes beautiful HTML email templates with:
- **Māori Cultural Styling**: Green color scheme and cultural elements
- **Priority Color Coding**: Different colors for different priority levels
- **Cultural Context Sections**: Special sections for cultural information
- **Responsive Design**: Works on desktop and mobile devices

## 🔐 Security Features

- **User Authentication**: All endpoints require authentication
- **Role-Based Access**: Admin-only endpoints for templates
- **Input Validation**: Pydantic schemas for data validation
- **Error Handling**: Comprehensive error handling and logging

## 🧪 Testing

### **Run All Tests**
```bash
cd backend
python test_notifications.py
```

### **Test Individual Components**
```python
# Test email sending
notification_service.send_email_notification(notification, user)

# Test SMS sending
notification_service.send_sms_notification(notification, user)

# Test low stock alerts
notification_service.create_low_stock_alert(item)

# Test cultural event reminders
notification_service.create_cultural_event_reminder(
    event_title="Matariki",
    event_date=datetime.now(),
    user_ids=[1, 2, 3]
)
```

## 📈 Monitoring

### **Notification Statistics**
- Total notifications sent
- Unread notifications count
- Failed notifications
- Notifications by type and priority

### **Health Checks**
- Email service connectivity
- SMS service connectivity
- Database connection status

## 🚀 Deployment

### **Production Considerations**
1. **Email Service**: Use a reliable SMTP service (SendGrid, Mailgun, etc.)
2. **SMS Service**: Ensure Twilio account has sufficient credits
3. **Database**: Monitor notification table size and performance
4. **Rate Limiting**: Implement rate limiting for notification endpoints
5. **Logging**: Set up proper logging for notification failures

### **Environment Variables**
```env
# Production Email (SendGrid example)
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key

# Production SMS
TWILIO_ACCOUNT_SID=your-production-sid
TWILIO_AUTH_TOKEN=your-production-token
TWILIO_FROM_NUMBER=+1234567890
```

## 🔄 Future Enhancements

### **Planned Features**
- **WebSocket Support**: Real-time push notifications
- **Notification Templates**: Customizable email and SMS templates
- **Scheduled Notifications**: Send notifications at specific times
- **Bulk Notifications**: Send to multiple users efficiently
- **Notification Analytics**: Detailed reporting and insights
- **Mobile App Integration**: Native mobile notifications

### **Cultural Enhancements**
- **Maramataka Integration**: Lunar calendar-based notifications
- **Iwi-Specific Notifications**: Custom notifications for different iwi
- **Cultural Protocol Alerts**: Reminders for cultural protocols
- **Whakapapa Notifications**: Genealogy-based notifications

## 🤝 Contributing

When contributing to the notification system:

1. **Follow Māori Cultural Protocols**: Respect cultural sensitivities
2. **Test Thoroughly**: Ensure all notification channels work
3. **Document Changes**: Update this documentation
4. **Consider Accessibility**: Ensure notifications are accessible
5. **Security First**: Validate all inputs and handle errors gracefully

## 📞 Support

For issues or questions about the notification system:

1. Check the test script output
2. Verify environment variable configuration
3. Review the API documentation at `/docs`
4. Check server logs for error details
5. Test individual notification channels

---

**Kia ora!** Thank you for using the Kaiwhakarite Rawa notification system - designed with respect for both modern technology and Māori cultural values.

**System Developer:** Merryh Dugenia Vecino 