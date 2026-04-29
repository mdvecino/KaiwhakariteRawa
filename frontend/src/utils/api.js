// IMPORTANT: Set REACT_APP_API_URL in your environment for production deployments.
import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Helper to extract error messages from API errors
function getErrorMessage(err) {
  const detail = err?.response?.data?.detail;
  if (!detail) return 'An error occurred';
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail.map(e => e.msg || JSON.stringify(e)).join(', ');
  if (typeof detail === 'object' && detail.msg) return detail.msg;
  return JSON.stringify(detail);
}

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only show critical errors as toasts
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      toast.error('Session expired. Please log in again.');
    } else if (error.response?.status >= 500) {
      // Don't show 500 errors as toasts - let individual components handle them
      console.error('Server error:', error.response?.status, error.response?.data);
    } else if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNABORTED') {
      // Network errors - let components handle them
      console.error('Network error:', error.message);
    }
    // Don't show other errors as toasts - let components handle them
    return Promise.reject(error);
  }
);

// API functions
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  me: () => api.get('/api/auth/me'),
};

export const inventoryAPI = {
  getAll: (params) => api.get('/api/inventory/', { params }),
  getById: (id) => api.get(`/api/inventory/${id}`),
  create: (data) => api.post('/api/inventory/', data),
  update: (id, data) => api.put(`/api/inventory/${id}`, data),
  delete: (id) => api.delete(`/api/inventory/${id}`),
  getMaoriItems: (params) => api.get('/api/inventory/maori/items', { params }),
  getStats: () => api.get('/api/inventory/stats'),
  getTapuItems: () => api.get('/api/inventory/tapu/items'),
  getLowStockItems: () => api.get('/api/inventory/low-stock/items'),
  getByBarcode: (barcode) => api.get(`/api/inventory/barcode/${barcode}`),
  getBySku: (sku) => api.get(`/api/inventory/sku/${sku}`),
  getTransactions: (itemId) => api.get(`/api/inventory/${itemId}/transactions`),
  getAllTransactions: (params) => api.get('/api/inventory/transactions/all', { params }),
  addTransaction: (itemId, data) => api.post(`/api/inventory/${itemId}/transactions`, data),
  uploadImage: (formData) => api.post('/api/inventory/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  // Cultural Features
  generateQRCode: (itemId) => api.get(`/api/inventory/${itemId}/qr-code`, { responseType: 'blob' }),
  getCulturalStory: (itemId) => api.get(`/api/inventory/${itemId}/cultural-story`),
  logCulturalAccess: (itemId, data) => api.post(`/api/inventory/${itemId}/cultural-access-log`, data),
};

export const suppliersAPI = {
  getAll: (params) => api.get('/api/suppliers/', { params }),
  getById: (id) => api.get(`/api/suppliers/${id}`),
  create: (data) => api.post('/api/suppliers/', data),
  update: (id, data) => api.put(`/api/suppliers/${id}`, data),
  delete: (id) => api.delete(`/api/suppliers/${id}`),
};

export const calendarAPI = {
  // Calendar Events
  getAll: (params) => api.get('/api/calendar/', { params }),
  getById: (id) => api.get(`/api/calendar/${id}`),
  create: (data) => api.post('/api/calendar/', data),
  update: (id, data) => api.put(`/api/calendar/${id}`, data),
  delete: (id) => api.delete(`/api/calendar/${id}`),
  
  // Māori Calendar Features
  getMonthData: (year, month) => api.get(`/api/calendar/month/${year}/${month}`),
  getDayData: (date) => api.get(`/api/calendar/day/${date}`),
  getTodayEvents: () => api.get('/api/calendar/today'),
  
  // Maramataka
  getMaramatakaDay: (date) => api.get(`/api/calendar/maramataka/${date}`),
  getMaramatakaMonth: (year, month) => api.get(`/api/calendar/maramataka/${year}/${month}`),
  createMaramatakaDay: (data) => api.post('/api/calendar/maramataka', data),
  
  // Cultural Events
  getCulturalEvents: () => api.get('/api/calendar/cultural'),
  getCulturalEventsForDate: (date) => api.get(`/api/calendar/cultural/${date}`),
  createCulturalEvent: (data) => api.post('/api/calendar/cultural', data),
  
  // Inventory Alerts
  getInventoryAlertsForDate: (date) => api.get(`/api/calendar/alerts/${date}`),
  createInventoryAlert: (data) => api.post('/api/calendar/alerts', data),
  
  // Setup
  initializeCulturalEvents: () => api.post('/api/calendar/setup/cultural-events'),
};

export const dashboardAPI = {
  getStats: () => api.get('/api/dashboard/stats'),
  getLowStockAlerts: () => api.get('/api/dashboard/low-stock-alerts'),
  getRecentActivity: () => api.get('/api/dashboard/recent-activity'),
  getCulturalAnalytics: () => api.get('/api/dashboard/cultural-analytics'),
  getTapuAlerts: () => api.get('/api/dashboard/tapu-alerts'),
};

export const usersAPI = {
  getAll: (params) => api.get('/api/users/', { params }),
  getById: (id) => api.get(`/api/users/${id}`),
  create: (data) => api.post('/api/users/', data),
  update: (id, data) => api.put(`/api/users/${id}`, data),
  delete: (id) => api.delete(`/api/users/${id}`),
  search: (params) => api.get('/api/users/search', { params }),
  getStats: () => api.get('/api/users/stats'),
  updateStatus: (id, status) => api.put(`/api/users/${id}/status`, { status }),
  resetPassword: (id) => api.post(`/api/users/${id}/reset-password`),
  me: () => api.get('/api/users/me'),
  updateMe: (data) => api.put('/api/users/me', data),
  uploadPhoto: (formData) => api.post('/api/users/me/upload-photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  changePassword: (data) => api.post('/api/users/me/change-password', data),
  getForMessaging: () => api.get('/api/users/messaging'),
};

export const reportsAPI = {
  exportCSV: () => api.get('/api/reports/export/csv'),
  getAnalytics: () => api.get('/api/reports/analytics'),
  getInventorySummary: () => api.get('/api/reports/inventory/summary'),
  getLowStockDetailed: () => api.get('/api/reports/inventory/low-stock-detailed'),
  getInventoryAnalytics: () => api.get('/api/reports/inventory/analytics'),
  getRevenueReport: () => api.get('/api/reports/revenue-report'),
};

export const settingsAPI = {
  get: () => api.get('/api/settings/'),
  update: (data) => api.put('/api/settings/', data),
};

export const notificationsAPI = {
  // Basic notification operations
  getAll: (params) => api.get('/api/notifications/', { params }),
  getUnread: () => api.get('/api/notifications/unread'),
  getStats: () => api.get('/api/notifications/stats'),
  create: (data) => api.post('/api/notifications/', data),
  createBulk: (data) => api.post('/api/notifications/bulk', data),
  
  // Notification management
  markAsRead: (id) => api.put(`/api/notifications/${id}/read`),
  markAllAsRead: () => api.put('/api/notifications/read-all'),
  
  // User preferences
  getPreferences: () => api.get('/api/notifications/preferences'),
  updatePreferences: (data) => api.put('/api/notifications/preferences', data),
  
  // Templates (Admin only)
  getTemplates: () => api.get('/api/notifications/templates'),
  createTemplate: (data) => api.post('/api/notifications/templates', data),
  updateTemplate: (id, data) => api.put(`/api/notifications/templates/${id}`, data),
  
  // Special notifications
  createLowStockAlert: (itemId) => api.post(`/api/notifications/low-stock-alert/${itemId}`),
  createCulturalEventReminder: (data) => api.post('/api/notifications/cultural-event-reminder', data),
  
  // Test
  test: () => api.post('/api/notifications/test'),
};

export const supplierReturnsAPI = {
  // Basic CRUD operations
  getAll: (params) => api.get('/api/supplier-returns/', { params }),
  getById: (id) => api.get(`/api/supplier-returns/${id}`),
  getByReturnId: (returnId) => api.get(`/api/supplier-returns/by-return-id/${returnId}`),
  create: (data) => api.post('/api/supplier-returns/', data),
  update: (id, data) => api.put(`/api/supplier-returns/${id}`, data),
  delete: (id) => api.delete(`/api/supplier-returns/${id}`),
  
  // Status management
  approve: (id, notes) => api.post(`/api/supplier-returns/${id}/approve`, { notes }),
  reject: (id, reason) => api.post(`/api/supplier-returns/${id}/reject`, { reason }),
  complete: (id, notes) => api.post(`/api/supplier-returns/${id}/complete`, { notes }),
  
  // Statistics
  getStats: (params) => api.get('/api/supplier-returns/stats/overview', { params }),
};

export const customersAPI = {
  getAll: (params) => api.get('/api/customers/', { params }),
  getById: (id) => api.get(`/api/customers/${id}`),
  create: (data) => api.post('/api/customers/', data),
  update: (id, data) => api.put(`/api/customers/${id}`, data),
  delete: (id) => api.delete(`/api/customers/${id}`),
  search: (params) => api.get('/api/customers/search', { params }),
};

export const customerReturnsAPI = {
  // Basic CRUD operations
  getAll: (params) => api.get('/api/customer-returns/', { params }),
  getById: (id) => api.get(`/api/customer-returns/${id}`),
  getByReturnId: (returnId) => api.get(`/api/customer-returns/${returnId}`),
  create: (data) => api.post('/api/customer-returns/', data),
  update: (id, data) => api.put(`/api/customer-returns/${id}`, data),
  delete: (id) => api.delete(`/api/customer-returns/${id}`),
  
  // Status management
  approve: (id, notes) => api.post(`/api/customer-returns/${id}/approve`, { notes }),
  reject: (id, reason) => api.post(`/api/customer-returns/${id}/reject`, { reason }),
  complete: (id, notes) => api.post(`/api/customer-returns/${id}/complete`, { notes }),
  
  // Statistics
  getStats: (params) => api.get('/api/customer-returns/stats/overview', { params }),
};

// Shared status color utility
export const getStatusColor = (status) => {
  // Normalize status to uppercase for consistency
  if (!status) return 'bg-gray-100 text-gray-800';
  const s = status.toString().toUpperCase();
  switch (s) {
    case 'ACTIVE':
    case 'COMPLETED':
      return 'bg-green-100 text-green-800';
    case 'INACTIVE':
    case 'CANCELLED':
      return 'bg-gray-100 text-gray-800';
    case 'SUSPENDED':
      return 'bg-red-100 text-red-800';
    case 'PENDING':
      return 'bg-yellow-100 text-yellow-800';
    case 'APPROVED':
      return 'bg-blue-100 text-blue-800';
    case 'REJECTED':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export const messagesAPI = {
  // Create new message
  createMessage: (messageData) => api.post('/api/messages/', messageData),
  
  // Send bulk messages
  sendBulkMessages: (bulkData) => api.post('/api/messages/bulk', bulkData),
  
  // Get all messages for current user
  getMessages: (limit = 50, offset = 0) => api.get(`/api/messages/?limit=${limit}&offset=${offset}`),
  
  // Get inbox messages
  getInboxMessages: (limit = 50, offset = 0) => api.get(`/api/messages/inbox?limit=${limit}&offset=${offset}`),
  
  // Get sent messages
  getSentMessages: (limit = 50, offset = 0) => api.get(`/api/messages/sent?limit=${limit}&offset=${offset}`),
  
  // Get unread messages
  getUnreadMessages: () => api.get('/api/messages/unread'),
  
  // Mark message as read
  markAsRead: (messageId) => api.put(`/api/messages/${messageId}/read`),
  
  // Mark all messages as read
  markAllAsRead: () => api.put('/api/messages/read-all'),
  
  // Archive message
  archiveMessage: (messageId) => api.put(`/api/messages/${messageId}/archive`),
  
  // Delete message
  deleteMessage: (messageId) => api.delete(`/api/messages/${messageId}`),
  
  // Search messages
  searchMessages: (searchData) => api.post('/api/messages/search', searchData),
  
  // Get message statistics
  getStats: () => api.get('/api/messages/stats'),
  
  // Thread operations
  createThread: (threadData) => api.post('/api/messages/threads', threadData),
  getThreads: (limit = 50, offset = 0) => api.get(`/api/messages/threads?limit=${limit}&offset=${offset}`),
  addThreadMessage: (threadId, messageData) => api.post(`/api/messages/threads/${threadId}/messages`, messageData),
  getThreadMessages: (threadId, limit = 100, offset = 0) => api.get(`/api/messages/threads/${threadId}/messages?limit=${limit}&offset=${offset}`),
  
  // Template operations
  getTemplates: () => api.get('/api/messages/templates'),
  createTemplate: (templateData) => api.post('/api/messages/templates', templateData),
  
  // Special message types
  sendInventoryMessage: (itemId, subject, content, recipientId, culturalContext) => 
    api.post(`/api/messages/inventory/${itemId}`, { subject, content, recipient_id: recipientId, cultural_context: culturalContext }),
  
  sendCulturalEventMessage: (eventId, subject, content, recipientId, culturalContext) => 
    api.post(`/api/messages/cultural-event/${eventId}`, { subject, content, recipient_id: recipientId, cultural_context: culturalContext })
};

export default api; 