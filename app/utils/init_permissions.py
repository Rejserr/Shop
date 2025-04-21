from app.models.permission import Permission
from app import db

def init_permissions():
    permissions_data = [
        # Navigation
        ('NAV_DASHBOARD', 'Access to Dashboard'),
        ('NAV_USERS', 'Access to Users Management'),
        ('NAV_BRANCHES', 'Access to Branches Management'),
        ('NAV_ROLES', 'Access to Roles Management'),
        ('NAV_ZAPRIMANJE', 'Access to Zaprimanje Management'),
        ('NAV_REPORTS', 'Access to Reports'),
        ('NAV_MSI_API', 'Access to MSI API'),
        ('NAV_BACKORDERS', 'Access to view and search backorders'),  # Add this line
        
        # Dashboard Stats
        ('VIEW_USERS_STATS', 'View Users Statistics'),
        ('VIEW_BRANCHES_STATS', 'View Branches Statistics'),
        ('VIEW_ORDERS_STATS', 'View Orders Statistics'),
        ('VIEW_DELIVERY_STATS', 'View Delivery Statistics'),
        ('VIEW_CONNECTED_USERS', 'View Connected Users'),
        
        # Management
        ('MANAGE_USERS', 'Can manage users'),
        ('MANAGE_BRANCHES', 'Can manage branches'),
        ('MANAGE_ROLES', 'Can manage roles'),
        ('MANAGE_PERMISSIONS', 'Can manage permissions'),
        
        # Actions
        ('CREATE_USER', 'Can create users'),
        ('EDIT_USER', 'Can edit users'),
        ('DELETE_USER', 'Can delete users'),
        ('CREATE_BRANCH', 'Can create branches'),
        ('EDIT_BRANCH', 'Can edit branches'),
        ('DELETE_BRANCH', 'Can delete branches'),
        
        # Zaprimanje
        ('ZAPRIMANJE_CREATE', 'Can create zaprimanje'),
        ('ZAPRIMANJE_EDIT', 'Can edit zaprimanje'),
        ('ZAPRIMANJE_DELETE', 'Can delete zaprimanje'),
        ('ZAPRIMANJE_COMPLETE', 'Can complete zaprimanje'),
        ('ZAPRIMANJE_VIEW', 'Can view zaprimanje'),
        
        # Backorders (Add these permissions for more granular control)
        ('BACKORDERS_VIEW', 'Can view backorders'),
        ('BACKORDERS_EXPORT', 'Can export backorders to CSV'),
        
        # Admin
        ('ADMIN', 'Full system access')
    ]    
    # Add or update permissions
    for perm_name, desc in permissions_data:
        permission = Permission.query.filter_by(permission_name=perm_name).first()
        if permission:
            permission.description = desc
        else:
            permission = Permission(permission_name=perm_name, description=desc)
            db.session.add(permission)
        db.session.commit()