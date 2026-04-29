# 📬 Messaging System Documentation

## Overview

The Kaiwhakarite Rawa messaging system provides comprehensive communication capabilities for users within the inventory management platform. It integrates Māori cultural values and supports both individual messages and group conversations (threads).

## 🌟 Features

### Core Messaging Features
- **Individual Messages**: Send direct messages to other users
- **Message Threads**: Create group conversations with multiple participants
- **Message Types**: General, Inventory, Cultural, Event, Urgent, System
- **Priority Levels**: Low, Medium, High, Urgent
- **Message Status**: Sent, Delivered, Read, Archived
- **Search & Filter**: Advanced search with multiple filters
- **Bulk Messaging**: Send messages to multiple recipients

### Cultural Integration
- **Cultural Context**: Add cultural significance to messages
- **Iwi Connections**: Link messages to specific tribal affiliations
- **Cultural Protocols**: Respect Māori communication protocols
- **Bilingual Support**: Support for both English and Māori content
- **Cultural Templates**: Pre-built templates for cultural communications

### Advanced Features
- **Message Templates**: Reusable templates for common messages
- **Inventory Integration**: Send messages related to specific inventory items
- **Event Integration**: Send messages related to cultural events
- **Response Tracking**: Track required responses and deadlines
- **Message Statistics**: Comprehensive analytics and reporting

## 🏗️ Architecture

### Database Models

#### Message Model
```python
class Message(BaseModel):
    subject: str
    content: str
    message_type: MessageType
    priority: MessagePriority
    status: MessageStatus
    sender_id: int
    recipient_id: int
    cultural_context: Optional[str]
    iwi_connection: Optional[str]
    related_item_id: Optional[int]
    related_event_id: Optional[int]
```

#### MessageThread Model
```python
class MessageThread(BaseModel):
    title: str
    description: Optional[str]
    thread_type: MessageType
    created_by_id: int
    participants: List[MessageThreadParticipant]
    cultural_context: Optional[str]
    iwi_connection: Optional[str]
```

#### ThreadMessage Model
```python
class ThreadMessage(BaseModel):
    content: str
    thread_id: int
    sender_id: int
    cultural_context: Optional[str]
    reply_to_id: Optional[int]
```

### API Endpoints

#### Message Endpoints
- `POST /api/messages/` - Create new message
- `POST /api/messages/bulk` - Send bulk messages
- `GET /api/messages/` - Get all messages
- `GET /api/messages/inbox` - Get inbox messages
- `GET /api/messages/sent` - Get sent messages
- `GET /api/messages/unread` - Get unread messages
- `PUT /api/messages/{id}/read` - Mark as read
- `PUT /api/messages/read-all` - Mark all as read
- `PUT /api/messages/{id}/archive` - Archive message
- `DELETE /api/messages/{id}` - Delete message
- `POST /api/messages/search` - Search messages
- `GET /api/messages/stats` - Get message statistics

#### Thread Endpoints
- `POST /api/messages/threads` - Create new thread
- `GET /api/messages/threads` - Get user threads
- `POST /api/messages/threads/{id}/messages` - Add thread message
- `GET /api/messages/threads/{id}/messages` - Get thread messages

#### Template Endpoints
- `GET /api/messages/templates` - Get message templates
- `POST /api/messages/templates` - Create template (admin only)

#### Special Endpoints
- `POST /api/messages/inventory/{item_id}` - Send inventory-related message
- `POST /api/messages/cultural-event/{event_id}` - Send event-related message

## 🚀 Getting Started

### Backend Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run Database Migration**
   ```bash
   python migrate_messages.py
   ```

3. **Start Backend Server**
   ```bash
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Frontend Server**
   ```bash
   npm start
   ```

3. **Access Messaging System**
   - Navigate to `/messages` in the application
   - Use the sidebar navigation to access the messaging system

## 📱 User Interface

### Main Messaging Page
- **Inbox**: View received messages
- **Sent**: View sent messages
- **Threads**: View group conversations
- **Archive**: View archived messages
- **Statistics**: View message analytics

### Compose Message
- **Recipient Selection**: Choose from available users
- **Message Type**: Select appropriate message category
- **Priority**: Set message priority level
- **Cultural Context**: Add cultural significance
- **Iwi Connection**: Link to tribal affiliations
- **Response Required**: Mark if response is needed

### Thread Management
- **Create Thread**: Start new group conversation
- **Add Participants**: Invite users to threads
- **Thread Messages**: View and send messages in threads
- **Thread Settings**: Manage thread permissions and settings

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///./kaiwhakarite_rawa.db

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS (optional)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=your-twilio-number
```

### Message Templates
The system includes pre-built templates:
- **Low Stock Alert**: Notify about inventory shortages
- **Cultural Event Reminder**: Remind about upcoming events
- **General Communication**: Standard communication template

## 📊 Usage Examples

### Sending a Message
```javascript
// Frontend API call
const messageData = {
  recipient_id: 2,
  subject: "Inventory Update Required",
  content: "Please review the current stock levels for traditional items.",
  message_type: "inventory",
  priority: "medium",
  cultural_context: "Proper inventory management ensures we can continue our cultural practices.",
  iwi_connection: "Ngāti Porou"
};

await messagesAPI.createMessage(messageData);
```

### Creating a Thread
```javascript
const threadData = {
  title: "Cultural Event Planning",
  description: "Discussion about upcoming Matariki celebrations",
  participant_ids: [1, 2, 3, 4],
  thread_type: "cultural",
  cultural_context: "Matariki is a time for reflection and community gathering.",
  iwi_connection: "Multiple iwi"
};

await messagesAPI.createThread(threadData);
```

### Sending Inventory-Related Message
```javascript
await messagesAPI.sendInventoryMessage(
  itemId,
  "Low Stock Alert",
  "This traditional item is running low on stock.",
  recipientId,
  "This item is important for our cultural ceremonies."
);
```

## 🎨 Cultural Integration

### Cultural Context
- Add cultural significance to messages
- Include traditional knowledge and practices
- Respect Māori communication protocols
- Support for bilingual content

### Iwi Connections
- Link messages to specific tribal affiliations
- Respect tribal boundaries and protocols
- Support for multi-iwi communications
- Cultural sensitivity in messaging

### Traditional Practices
- Respect for tapu (sacred) communications
- Proper use of karakia (prayers) when appropriate
- Cultural protocols for group communications
- Traditional greeting and farewell practices

## 🔒 Security & Permissions

### User Permissions
- **Admin**: Full access to all messaging features
- **Manager**: Can create threads and send bulk messages
- **User**: Can send individual messages and participate in threads

### Message Privacy
- Private messages between users
- Thread privacy settings
- Archive and delete capabilities
- Secure message storage

### Data Protection
- Encrypted message storage (optional)
- Secure API endpoints
- User authentication required
- Audit trail for message activities

## 📈 Analytics & Reporting

### Message Statistics
- Total messages sent/received
- Unread message count
- Messages by type and priority
- Recent activity tracking
- User engagement metrics

### Cultural Analytics
- Cultural message frequency
- Iwi connection tracking
- Cultural event communications
- Traditional knowledge sharing metrics

## 🛠️ Development

### Adding New Message Types
1. Update `MessageType` enum in `backend/models/messages.py`
2. Add corresponding frontend handling
3. Update templates and UI components
4. Test with cultural context

### Custom Templates
1. Create template in database
2. Add template variables
3. Update frontend template selection
4. Test template rendering

### Cultural Features
1. Add new cultural context fields
2. Update validation rules
3. Enhance UI for cultural elements
4. Test with Māori content

## 🧪 Testing

### Backend Testing
```bash
# Test message creation
python -c "
from backend.services.message_service import MessageService
from backend.schemas.messages import MessageCreate
from backend.db import get_db

db = next(get_db())
service = MessageService(db)
message_data = MessageCreate(
    recipient_id=2,
    subject='Test Message',
    content='This is a test message with cultural context.',
    cultural_context='Testing cultural integration.'
)
message = service.create_message(message_data, 1)
print(f'Message created: {message.id}')
"
```

### Frontend Testing
- Test message composition
- Test thread creation
- Test cultural context fields
- Test message templates
- Test search and filtering

## 🚀 Future Enhancements

### Planned Features
- **Real-time Messaging**: WebSocket integration for live chat
- **File Attachments**: Support for images and documents
- **Voice Messages**: Audio message support
- **Message Encryption**: End-to-end encryption
- **Advanced Search**: Full-text search with cultural context
- **Message Scheduling**: Send messages at specific times
- **Cultural Calendar Integration**: Automatic cultural event reminders
- **Māori Language Support**: Full bilingual interface

### Cultural Enhancements
- **Traditional Greetings**: Automatic cultural greetings
- **Seasonal Messages**: Messages based on Māori calendar
- **Cultural Protocols**: Automated cultural protocol reminders
- **Iwi-specific Features**: Custom features for different iwi
- **Traditional Knowledge Sharing**: Structured cultural knowledge exchange

## 📞 Support

For technical support or questions about the messaging system:
- Check the API documentation at `/docs` when the server is running
- Review the database schema for detailed field information
- Test the system using the provided examples
- Contact the development team for cultural guidance

## 📝 License

This messaging system is part of the Kaiwhakarite Rawa inventory management platform and follows the same licensing terms as the main application.

---

**System Developer**: Merryh Dugenia Vecino  
**Last Updated**: July 2025  
**Version**: 1.0.0 