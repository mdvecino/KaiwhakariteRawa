# Kaiwhakarite Rawa Frontend

A modern React frontend for the Kaiwhakarite Rawa inventory and resource management system with Māori cultural integration.

## Features

### 🎨 **Modern UI/UX**
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Māori Green Theme**: Beautiful fern-inspired color palette (#3A7256, #81C784, #1B4332)
- **Dark/Light Mode**: Toggle between themes with persistent preferences
- **Smooth Animations**: CSS transitions and micro-interactions for better UX

### 🌏 **Bilingual Support**
- **English/Te Reo Māori**: Complete language switching throughout the application
- **Cultural Integration**: Māori terminology and cultural elements
- **Accessible Design**: WCAG compliant with proper contrast ratios

### 🔐 **Authentication & Security**
- **JWT Authentication**: Secure login with token-based sessions
- **Role-Based Access**: Admin, Manager, and User roles with appropriate permissions
- **Protected Routes**: Automatic redirection for unauthorized access
- **Session Management**: Persistent login state with automatic token refresh

### 📊 **Dashboard & Analytics**
- **Real-time Statistics**: Live inventory counts, values, and alerts
- **Interactive Charts**: Visual data representation with Recharts
- **Quick Actions**: Fast access to common tasks
- **Recent Activity**: Timeline of system events

### 📦 **Inventory Management**
- **Full CRUD Operations**: Create, Read, Update, Delete inventory items
- **Barcode Integration**: Generate and scan barcodes with JsBarcode
- **Advanced Search**: Filter by category, location, supplier, and more
- **Stock Alerts**: Low stock notifications and reorder points

### 🍃 **Māori Cultural Features**
- **Māori Items Section**: Dedicated space for cultural artifacts
- **Tapu Status**: Respect for sacred items and protocols
- **Kōrero Fields**: Story and narrative preservation
- **Whakapapa Integration**: Genealogical connections
- **Karakia Support**: Prayer and blessing documentation

### 📅 **Calendar Integration**
- **Māori Calendar**: Traditional lunar calendar integration
- **Event Management**: Cultural events and ceremonies
- **Reminder System**: Important dates and notifications

### 📈 **Reporting & Analytics**
- **Export Functionality**: CSV export for data analysis
- **Visual Reports**: Charts and graphs for insights
- **Custom Filters**: Date ranges, categories, and suppliers

## Technology Stack

- **React 18**: Modern React with hooks and functional components
- **Tailwind CSS**: Utility-first CSS framework with custom Māori theme
- **React Router**: Client-side routing with protected routes
- **React Query**: Server state management and caching
- **Axios**: HTTP client for API communication
- **Lucide React**: Beautiful, customizable icons
- **React Hook Form**: Performant forms with validation
- **React Hot Toast**: Elegant notifications
- **JsBarcode**: Barcode generation and scanning
- **Recharts**: Composable charting library

## Getting Started

### Prerequisites

- **Node.js** (v16 or higher)
- **npm** (v8 or higher)
- **Backend Server**: Ensure the FastAPI backend is running on `http://localhost:8000`

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd KaiwhakariteRawa_v3/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

   Or use the provided batch script on Windows:
   ```bash
   start_frontend.bat
   ```

4. **Open your browser** and navigate to `http://localhost:3000`

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_VERSION=1.0.0
```

## Project Structure

```
frontend/
├── public/                 # Static assets
│   ├── index.html         # Main HTML template
│   └── favicon.ico        # App icon
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Layout.jsx     # Main layout with sidebar
│   │   ├── Header.jsx     # Top navigation bar
│   │   ├── Sidebar.jsx    # Side navigation
│   │   └── LoadingSpinner.jsx
│   ├── context/           # React Context providers
│   │   ├── AuthContext.jsx    # Authentication state
│   │   └── ThemeContext.jsx   # Theme and language
│   ├── pages/             # Page components
│   │   ├── Login.jsx      # Authentication page
│   │   ├── Dashboard.jsx  # Main dashboard
│   │   ├── Inventory.jsx  # Inventory management
│   │   ├── MaoriItems.jsx # Cultural items
│   │   ├── Suppliers.jsx  # Supplier management
│   │   ├── Calendar.jsx   # Event calendar
│   │   ├── Reports.jsx    # Analytics and reports
│   │   └── Settings.jsx   # User preferences
│   ├── utils/             # Utility functions
│   │   ├── api.js         # API client and endpoints
│   │   └── translations.js # Bilingual text
│   ├── App.jsx            # Main app component
│   ├── index.js           # React entry point
│   └── index.css          # Global styles and Tailwind
├── package.json           # Dependencies and scripts
├── tailwind.config.js     # Tailwind configuration
└── postcss.config.js      # PostCSS configuration
```

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run test suite
- `npm eject` - Eject from Create React App

## Demo Credentials

Use these credentials to test the system:

- **Admin**: `admin` / `admin123`
- **Manager**: `manager` / `manager123`
- **User**: `user` / `user123`

## Cultural Integration

### Māori Design Elements

- **Color Palette**: Inspired by native ferns and flax
- **Typography**: Clean, readable fonts with Māori language support
- **Icons**: Cultural symbols and natural elements
- **Patterns**: Subtle Māori-inspired background patterns

### Cultural Features

- **Tapu Respect**: Special handling for sacred items
- **Kōrero Preservation**: Story and narrative fields
- **Whakapapa**: Genealogical connections and history
- **Karakia**: Prayer and blessing documentation
- **Māori Calendar**: Traditional lunar calendar integration

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow the existing code style and patterns
2. Ensure all new features include both English and Māori translations
3. Test on multiple devices and screen sizes
4. Maintain cultural sensitivity in all implementations

## License

This project is part of the Kaiwhakarite Rawa system and follows the same licensing terms.

## Support

For technical support or questions about Māori cultural integration, please refer to the main project documentation. 