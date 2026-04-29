# Deployment Guide - Kaiwhakarite Rawa

This guide explains how to deploy the Kaiwhakarite Rawa system to Render (backend) and Vercel (frontend).

## 🗄️ Database Location

The SQLite database (`kaiwhakarite_rawa.db`) is located in the **root directory** to ensure compatibility with cloud deployment platforms. This allows the backend services to access the database file properly.

## 🚀 Render Deployment (Backend)

### Prerequisites
- Render account
- GitHub repository with your code

### Deployment Steps

1. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Choose the repository containing your project

2. **Configure the Service**
   - **Name**: `kaiwhakarite-rawa-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python run_server.py`
   - **Root Directory**: Leave empty (use repository root)

3. **Environment Variables**
   ```
   PYTHON_VERSION=3.11
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy your backend

### Backend URL
Your backend will be available at: `https://your-service-name.onrender.com`

### Health Check Endpoints
Your backend includes comprehensive health check endpoints:
- Basic health: `https://your-service-name.onrender.com/health`
- Detailed health: `https://your-service-name.onrender.com/health/detailed`
- Database health: `https://your-service-name.onrender.com/health/database`
- System resources: `https://your-service-name.onrender.com/health/resources`

## 🌐 Vercel Deployment (Frontend)

### Prerequisites
- Vercel account
- GitHub repository with your code

### Deployment Steps

1. **Import Project to Vercel**
   - Connect your GitHub repository
   - Choose the repository containing your project

2. **Configure the Project**
   - **Framework Preset**: `Create React App`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

3. **Environment Variables**
   ```
   REACT_APP_API_URL=https://your-backend-url.onrender.com
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will automatically deploy your frontend

### Frontend URL
Your frontend will be available at: `https://your-project-name.vercel.app`

## 🔧 Configuration Updates

### Frontend API Configuration
Update `frontend/src/utils/api.js` to use your backend URL:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

### CORS Configuration
Ensure your backend allows requests from your Vercel domain:

```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-project-name.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Database Considerations

### SQLite in Production
- SQLite is suitable for small to medium applications
- For larger scale, consider migrating to PostgreSQL
- Render supports PostgreSQL databases

### Database Persistence
- The SQLite file will persist between deployments
- Consider backing up the database regularly
- For production, use a managed database service

## 🔍 Troubleshooting

### Common Issues

1. **Backend not starting**
   - Check the build command includes `cd backend`
   - Verify all dependencies are in `backend/requirements.txt`

2. **Frontend can't connect to backend**
   - Verify the API URL in environment variables
   - Check CORS configuration in backend

3. **Database connection errors**
   - Ensure database file is in root directory
   - Check file permissions on the database

### Logs
- Render: Check logs in the Render dashboard
- Vercel: Check logs in the Vercel dashboard

## 📝 Environment Variables Reference

### Backend (Render)
```
PYTHON_VERSION=3.11
```

### Frontend (Vercel)
```
REACT_APP_API_URL=https://your-backend-url.onrender.com
```

## 🎯 Next Steps

1. Deploy backend to Render
2. Deploy frontend to Vercel
3. Update API URLs in frontend
4. Test the complete system
5. Set up monitoring and logging
6. Configure custom domains (optional) 