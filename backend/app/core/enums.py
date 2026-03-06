"""
Core enumerations for the application
"""
from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class SubscriptionPlan(str, Enum):
    """Subscription plan types"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class UsageAction(str, Enum):
    """Types of usage actions to track"""
    OPTIMIZATION_RUN = "optimization_run"
    CSV_UPLOAD = "csv_upload"
    PRODUCT_CREATE = "product_create"
    BOX_CREATE = "box_create"
    DATA_EXPORT = "data_export"
    API_CALL = "api_call"


class AuditAction(str, Enum):
    """Types of audit actions"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PRODUCT_CREATE = "product_create"
    PRODUCT_UPDATE = "product_update"
    PRODUCT_DELETE = "product_delete"
    BOX_CREATE = "box_create"
    BOX_UPDATE = "box_update"
    BOX_DELETE = "box_delete"
    SUBSCRIPTION_CHANGE = "subscription_change"
    ROLE_GRANT = "role_grant"
    ROLE_REVOKE = "role_revoke"
    SETTINGS_UPDATE = "settings_update"
    DATA_EXPORT = "data_export"
