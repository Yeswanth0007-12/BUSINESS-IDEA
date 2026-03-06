"""
RBAC Permissions System
"""
from typing import Set
from app.core.enums import UserRole


class Permission:
    """Permission definitions"""
    # Product permissions
    VIEW_PRODUCTS = "view_products"
    CREATE_PRODUCTS = "create_products"
    EDIT_PRODUCTS = "edit_products"
    DELETE_PRODUCTS = "delete_products"
    
    # Box permissions
    VIEW_BOXES = "view_boxes"
    CREATE_BOXES = "create_boxes"
    EDIT_BOXES = "edit_boxes"
    DELETE_BOXES = "delete_boxes"
    
    # Optimization permissions
    RUN_OPTIMIZATION = "run_optimization"
    VIEW_OPTIMIZATION_HISTORY = "view_optimization_history"
    
    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"
    VIEW_ADVANCED_ANALYTICS = "view_advanced_analytics"
    
    # Export permissions
    EXPORT_DATA = "export_data"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_SUBSCRIPTION = "manage_subscription"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SETTINGS = "manage_settings"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[UserRole, Set[str]] = {
    UserRole.ADMIN: {
        # All permissions
        Permission.VIEW_PRODUCTS,
        Permission.CREATE_PRODUCTS,
        Permission.EDIT_PRODUCTS,
        Permission.DELETE_PRODUCTS,
        Permission.VIEW_BOXES,
        Permission.CREATE_BOXES,
        Permission.EDIT_BOXES,
        Permission.DELETE_BOXES,
        Permission.RUN_OPTIMIZATION,
        Permission.VIEW_OPTIMIZATION_HISTORY,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_ADVANCED_ANALYTICS,
        Permission.EXPORT_DATA,
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.MANAGE_SUBSCRIPTION,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_SETTINGS,
    },
    UserRole.ANALYST: {
        # Read + Create + Optimize
        Permission.VIEW_PRODUCTS,
        Permission.CREATE_PRODUCTS,
        Permission.EDIT_PRODUCTS,
        Permission.VIEW_BOXES,
        Permission.CREATE_BOXES,
        Permission.EDIT_BOXES,
        Permission.RUN_OPTIMIZATION,
        Permission.VIEW_OPTIMIZATION_HISTORY,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_ADVANCED_ANALYTICS,
        Permission.EXPORT_DATA,
    },
    UserRole.VIEWER: {
        # Read only
        Permission.VIEW_PRODUCTS,
        Permission.VIEW_BOXES,
        Permission.RUN_OPTIMIZATION,
        Permission.VIEW_OPTIMIZATION_HISTORY,
        Permission.VIEW_ANALYTICS,
    },
}


def has_permission(role: UserRole, permission: str) -> bool:
    """Check if a role has a specific permission"""
    return permission in ROLE_PERMISSIONS.get(role, set())


def get_role_permissions(role: UserRole) -> Set[str]:
    """Get all permissions for a role"""
    return ROLE_PERMISSIONS.get(role, set())
