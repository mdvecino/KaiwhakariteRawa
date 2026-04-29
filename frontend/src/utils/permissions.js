// Permission utility system for Kaiwhakarite Rawa

// Permission constants
export const PERMISSIONS = {
  // User Management
  USERS_VIEW: 'users.view',
  USERS_CREATE: 'users.create',
  USERS_EDIT: 'users.edit',
  USERS_DELETE: 'users.delete',
  USERS_RESET_PASSWORD: 'users.reset_password',
  
  // Settings
  SETTINGS_VIEW: 'settings.view',
  SETTINGS_EDIT: 'settings.edit',
  
  // Inventory
  INVENTORY_VIEW: 'inventory.view',
  INVENTORY_CREATE: 'inventory.create',
  INVENTORY_EDIT: 'inventory.edit',
  INVENTORY_DELETE: 'inventory.delete',
  
  // Reports
  REPORTS_VIEW: 'reports.view',
  REPORTS_EXPORT: 'reports.export',
  REPORTS_CONFIGURE: 'reports.configure',
  
  // Transactions
  TRANSACTIONS_VIEW: 'transactions.view',
  TRANSACTIONS_CREATE: 'transactions.create',
  TRANSACTIONS_EDIT: 'transactions.edit',
  TRANSACTIONS_DELETE: 'transactions.delete',
};

// Role-based permission mapping
export const ROLE_PERMISSIONS = {
  ADMIN: [
    // Full permissions for everything
    PERMISSIONS.USERS_VIEW,
    PERMISSIONS.USERS_CREATE,
    PERMISSIONS.USERS_EDIT,
    PERMISSIONS.USERS_DELETE,
    PERMISSIONS.USERS_RESET_PASSWORD,
    
    PERMISSIONS.SETTINGS_VIEW,
    PERMISSIONS.SETTINGS_EDIT,
    
    PERMISSIONS.INVENTORY_VIEW,
    PERMISSIONS.INVENTORY_CREATE,
    PERMISSIONS.INVENTORY_EDIT,
    PERMISSIONS.INVENTORY_DELETE,
    
    PERMISSIONS.REPORTS_VIEW,
    PERMISSIONS.REPORTS_EXPORT,
    PERMISSIONS.REPORTS_CONFIGURE,
    
    PERMISSIONS.TRANSACTIONS_VIEW,
    PERMISSIONS.TRANSACTIONS_CREATE,
    PERMISSIONS.TRANSACTIONS_EDIT,
    PERMISSIONS.TRANSACTIONS_DELETE,
  ],
  
  MANAGER: [
    // Limited permissions
    PERMISSIONS.USERS_VIEW, // Can view users but not edit
    
    PERMISSIONS.SETTINGS_VIEW, // Can view settings but not edit
    
    PERMISSIONS.INVENTORY_VIEW,
    PERMISSIONS.INVENTORY_CREATE,
    PERMISSIONS.INVENTORY_EDIT,
    // No delete permission for inventory
    
    PERMISSIONS.REPORTS_VIEW,
    PERMISSIONS.REPORTS_EXPORT,
    // No configure permission for reports
    
    PERMISSIONS.TRANSACTIONS_VIEW,
    PERMISSIONS.TRANSACTIONS_CREATE,
    PERMISSIONS.TRANSACTIONS_EDIT,
    PERMISSIONS.TRANSACTIONS_DELETE,
  ],
  
  USER: [
    // Enhanced permissions for USER role
    PERMISSIONS.INVENTORY_VIEW,
    PERMISSIONS.INVENTORY_CREATE,
    PERMISSIONS.INVENTORY_EDIT, // Allow editing
    
    PERMISSIONS.REPORTS_VIEW,
    PERMISSIONS.REPORTS_EXPORT, // Allow export
    
    // Add access to more modules
    'customers.view',
    'customers.create',
    'customers.edit',
    
    'suppliers.view',
    'suppliers.create', 
    'suppliers.edit',
    
    'stock-locations.view',
    'stock-locations.create',
    'stock-locations.edit',
    
    'maori-items.view',
    'maori-items.create',
    'maori-items.edit',
    
    'calendar.view',
    'calendar.create',
    'calendar.edit',
    
    'customer-returns.view',
    'customer-returns.create',
    'customer-returns.edit',
    
    // No user management access
    // No settings access
    // No transactions access (admin/manager only)
  ]
};

// Check if user has specific permission
export const hasPermission = (user, permission) => {
  if (!user || !user.role) return false;
  
  const userRole = user.role.toUpperCase();
  const rolePermissions = ROLE_PERMISSIONS[userRole] || [];
  
  return rolePermissions.includes(permission);
};

// Check if user has any of the specified permissions
export const hasAnyPermission = (user, permissions) => {
  return permissions.some(permission => hasPermission(user, permission));
};

// Check if user has all of the specified permissions
export const hasAllPermissions = (user, permissions) => {
  return permissions.every(permission => hasPermission(user, permission));
};

// Get user's role display name
export const getRoleDisplayName = (user) => {
  if (!user || !user.role) return 'Unknown';
  
  const roleNames = {
    ADMIN: 'Administrator',
    MANAGER: 'Manager',
    USER: 'User'
  };
  
  return roleNames[user.role.toUpperCase()] || user.role;
};

// Check if user has read-only access to a module
export const isReadOnlyAccess = (user, module) => {
  if (!user || !user.role) return true;
  
  const userRole = user.role.toUpperCase();
  
  // Define read-only modules for each role
  const readOnlyModules = {
    ADMIN: [], // Admin has full access to everything
    MANAGER: ['User Management', 'Settings'], // Manager has read-only access to these
    USER: [] // User has full access to permitted modules, just can't access User Management and Settings at all
  };
  
  return (readOnlyModules[userRole] || []).includes(module);
};

export default {
  PERMISSIONS,
  ROLE_PERMISSIONS,
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  getRoleDisplayName,
  isReadOnlyAccess
}; 