# Kaiwhakarite Rawa - Inventory and Resource Management System

A comprehensive inventory and resource management system with Māori cultural integration, built with FastAPI backend and React frontend. Designed to handle both general inventory items and Māori cultural artifacts with respect and proper protocols.

## 🌟 Features

### Core Functionality
- **Full CRUD Operations** for inventory items, suppliers, users, and calendar events
- **Māori Cultural Integration** with iwi, tapu status, kōrero, and whakapapa fields
- **Role-based Access Control** (Admin, Manager, User)
- **JWT Authentication** with secure password hashing
- **Barcode Generation and Scanning** support
- **Photo Upload** for inventory items
- **Māori Calendar Integration** (Matariki, Maramataka events)

### Frontend Features
- **Modern React UI** with Tailwind CSS and Māori green theme
- **Responsive Design** for desktop, tablet, and mobile
- **Dark/Light Mode** with persistent preferences
- **Bilingual Support** (English/Te Reo Māori)
- **Real-time Dashboard** with statistics and alerts
- **Interactive Charts** and data visualization

### Technical Features
- **FastAPI Backend** with automatic API documentation
- **React Frontend** with modern hooks and context
- **SQLite Database** with SQLAlchemy ORM
- **Pydantic Data Validation**
- **CORS Support** for frontend integration
- **Static File Serving** for uploaded images
- **Comprehensive Error Handling**

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- npm 8+

### Option 1: Automatic Setup (Windows)

Use the provided batch script to start both servers:

```bash
start_system.bat
```

This will start both backend and frontend servers automatically.

### Option 2: Manual Setup

#### Backend Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd KaiwhakariteRawa_v3
   ```

2. **Navigate to backend directory and install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start the backend server**
   ```bash
   python run_server.py
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the frontend server**
   ```bash
   npm start
   ```

### Access Points

Once both servers are running:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Demo Credentials

Use these credentials to test the system:

- **Admin**: `admin` / `admin123`
- **Manager**: `manager` / `manager123`
- **User**: `user` / `user123`

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Inventory Endpoints
- `GET /api/inventory/` - List all inventory items
- `POST /api/inventory/` - Create new inventory item
- `GET /api/inventory/{item_id}` - Get specific item
- `PUT /api/inventory/{item_id}` - Update item
- `DELETE /api/inventory/{item_id}` - Delete item
- `GET /api/inventory/maori/items` - Get Māori cultural items
- `GET /api/inventory/tapu/items` - Get tapu items
- `GET /api/inventory/low-stock/items` - Get low stock alerts

### Dashboard Endpoints
- `GET /api/dashboard/stats` - Get system statistics
- `GET /api/dashboard/low-stock-alerts` - Get low stock alerts
- `GET /api/dashboard/recent-activity` - Get recent activity

### User Management (Admin Only)
- `GET /api/users/` - List all users
- `GET /api/users/{user_id}` - Get specific user
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user

### Supplier Management
- `GET /api/suppliers/` - List all suppliers
- `POST /api/suppliers/` - Create new supplier
- `GET /api/suppliers/{supplier_id}` - Get specific supplier
- `PUT /api/suppliers/{supplier_id}` - Update supplier
- `DELETE /api/suppliers/{supplier_id}` - Delete supplier

### Calendar Events
- `GET /api/calendar/` - List all events
- `POST /api/calendar/` - Create new event
- `GET /api/calendar/{event_id}` - Get specific event
- `PUT /api/calendar/{event_id}` - Update event
- `DELETE /api/calendar/{event_id}` - Delete event

## 🗄️ Database Schema

### Users Table
- `id`, `username`, `email`, `hashed_password`, `full_name`
- `role` (admin/manager/user), `profile_image`, `two_factor_enabled`
- `last_login`, `created_at`, `updated_at`, `is_active`

### Inventory Items Table
- Basic fields: `name`, `description`, `sku`, `barcode`, `category`
- Quantity: `quantity`, `min_quantity`, `max_quantity`, `location`
- Financial: `unit_cost`, `total_value`, `supplier_id`
- Status: `status`, `condition_notes`, `maintenance_schedule`
- **Māori Cultural Fields**: `iwi`, `tapu_status`, `korero`, `whakapapa`, `tikanga_notes`
- Media: `image_url`, `documents`

### Suppliers Table
- `name`, `contact_person`, `email`, `phone`, `address`, `website`
- Business: `abn`, `tax_id`, `payment_terms`, `credit_limit`
- Status: `is_active`, `notes`, `rating`

### Calendar Events Table
- Basic: `title`, `description`, `event_type`, `start_date`, `end_date`
- Settings: `all_day`, `recurring`, `location`, `attendees`
- **Māori Cultural Fields**: `iwi_connection`, `cultural_significance`, `tikanga_requirements`
- Related: `related_items`, `is_public`, `requires_approval`

## 🎨 Cultural Integration

### Māori Cultural Fields
- **Iwi**: Tribal affiliation for cultural items
- **Tapu Status**: Sacred/protected status indicator
- **Kōrero**: Cultural narrative and stories
- **Whakapapa**: Genealogy and lineage information
- **Tikanga Notes**: Cultural protocols and requirements

### Event Types
- **Matariki**: Māori New Year celebrations
- **Maramataka**: Lunar calendar events
- **Cultural**: General cultural events
- **Maintenance**: Equipment maintenance schedules
- **Inventory**: Inventory-related events

## 🔐 Security Features

- **JWT Token Authentication** with configurable expiration
- **Password Hashing** using bcrypt
- **Role-based Access Control** with granular permissions
- **CORS Protection** for cross-origin requests
- **Input Validation** using Pydantic models

## 🚀 Deployment

### Database Location
The SQLite database (`kaiwhakarite_rawa.db`) is located in the root directory to ensure compatibility with cloud deployment platforms like Render and Vercel. This allows the database to be properly accessed by the backend services.

### Render Deployment
- Backend: Deploy the `backend/` directory as a Python service
- Database: The SQLite file in the root will be accessible
- Environment: Set up Python dependencies from `backend/requirements.txt`

### Vercel Deployment  
- Frontend: Deploy the `frontend/` directory as a Node.js application
- Build Command: `npm run build`
- Output Directory: `build/`

## 🛠️ Development
```
KaiwhakariteRawa_v3/
├── backend/                 # Backend Python files
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── db.py                # Database configuration
│   ├── run_server.py        # Server startup script
│   ├── comprehensive_test.py # System testing script
│   ├── requirements.txt     # Python dependencies
│   ├── start_backend_simple.bat # Backend startup script
│   ├── auth/                # Authentication modules
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic
│   └── scripts/             # Database scripts
├── frontend/                # Frontend React files
│   ├── package.json         # Node.js dependencies
│   ├── start_frontend_simple.bat # Frontend startup script
│   ├── src/                 # React source code
│   ├── public/              # Static assets
│   └── build/               # Production build
├── kaiwhakarite_rawa.db     # SQLite database (root for deployment)
├── uploads/                 # File uploads directory
├── start_system.bat         # Main system startup script
├── start_full_system.bat    # Full system startup (legacy)
├── start_system_fixed.bat   # Fixed system startup (legacy)
└── README.md               # Project documentation
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── routers/             # API endpoints
│   ├── auth/                # Authentication
│   └── uploads/             # File uploads
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── context/         # React Context providers
│   │   └── utils/           # Utility functions
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
├── requirements.txt         # Python dependencies
├── run_server.py           # Backend startup script
├── start_full_system.bat   # Full system startup (Windows)
├── test_full_system.py     # System testing script
└── README.md               # This file
```

### Testing
```bash
# Test the full system
python test_full_system.py

# Test imports
python test_imports.py

# Test connection
python backend/test_connection.py
```

### Database
The system uses SQLite by default (`kaiwhakarite_rawa.db`). For production, consider using PostgreSQL or MySQL.

## 🌐 Frontend Integration

The backend is designed to work with a React frontend. Key integration points:

- **CORS** is configured for `http://localhost:3000` and `http://localhost:3001`
- **JWT tokens** should be included in Authorization headers
- **File uploads** are served from `/uploads/` endpoint
- **API documentation** is available at `/docs`

## 📝 Environment Variables

Create a `.env` file for production settings:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./kaiwhakarite_rawa.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Include Māori cultural considerations
4. Test all endpoints

## 📄 License

This project is designed for cultural and educational purposes. Please respect Māori cultural protocols and consult with appropriate cultural advisors when implementing features related to Māori cultural items.

## 🆘 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the health endpoint at `/health`
3. Check server logs for error details

---

**Kia ora!** Thank you for using Kaiwhakarite Rawa - a system built with respect for both modern technology and Māori cultural values. 

# Kaiwhakarite Rawa

## Upholding the Four Ps of Māori Cultural Principles

**Our system is designed to honor the core principles of Te Tiriti o Waitangi and Māori cultural frameworks:**

- **Partnership (Te Rangapū):** Collaborative design, shared decision-making, and respect for Māori data sovereignty.
- **Participation (Te Whai Wāhitanga):** Inclusive, bilingual user experience and active engagement of all users.
- **Protection (Te Tiaki):** Secure handling of cultural information, respect for tapu (sacred) items, and robust data protection.
- **Permission (Mana Whakahaere):** Role-based access control ensures that users and communities have appropriate authority over their data and actions within the system.

*I hangaia tēnei pūnaha kia ū ki ngā mātāpono matua o Te Tiriti o Waitangi me ngā tikanga Māori: Te Rangapū, Te Whai Wāhitanga, Te Tiaki, me te Mana Whakahaere.*

**We are committed to ongoing learning and welcome feedback from Māori communities and users to further strengthen these principles.** 