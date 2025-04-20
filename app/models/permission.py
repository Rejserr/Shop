from enum import Enum
from app.extensions import db

class PermissionType(Enum):
    # Navigation Permissions
    NAV_DASHBOARD = 'NAV_DASHBOARD'
    NAV_USERS = 'NAV_USERS'
    NAV_BRANCHES = 'NAV_BRANCHES'
    NAV_ROLES = 'NAV_ROLES'
    NAV_ZAPRIMANJE = 'NAV_ZAPRIMANJE'
    NAV_REPORTS = 'NAV_REPORTS'
    
    # Dashboard Stats Permissions
    VIEW_USERS_STATS = 'VIEW_USERS_STATS'
    VIEW_BRANCHES_STATS = 'VIEW_BRANCHES_STATS'
    VIEW_ORDERS_STATS = 'VIEW_ORDERS_STATS'
    VIEW_DELIVERY_STATS = 'VIEW_DELIVERY_STATS'
    VIEW_CONNECTED_USERS = 'VIEW_CONNECTED_USERS'
    
    # Management Permissions
    MANAGE_USERS = 'MANAGE_USERS'
    MANAGE_BRANCHES = 'MANAGE_BRANCHES'
    MANAGE_ROLES = 'MANAGE_ROLES'
    MANAGE_PERMISSIONS = 'MANAGE_PERMISSIONS'
    
    # Action Permissions
    CREATE_USER = 'CREATE_USER'
    EDIT_USER = 'EDIT_USER'
    DELETE_USER = 'DELETE_USER'
    CREATE_BRANCH = 'CREATE_BRANCH'
    EDIT_BRANCH = 'EDIT_BRANCH'
    DELETE_BRANCH = 'DELETE_BRANCH'
    
    # Zaprimanje Permissions
    ZAPRIMANJE_CREATE = 'ZAPRIMANJE_CREATE'
    ZAPRIMANJE_EDIT = 'ZAPRIMANJE_EDIT'
    ZAPRIMANJE_DELETE = 'ZAPRIMANJE_DELETE'
    ZAPRIMANJE_COMPLETE = 'ZAPRIMANJE_COMPLETE'
    ZAPRIMANJE_VIEW = 'ZAPRIMANJE_VIEW'
from app.extensions import db

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    permission_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<Permission {self.permission_name}>'

    @staticmethod
    def get_permission_by_name(permission_name):
        return Permission.query.filter_by(permission_name=permission_name).first()

    @staticmethod
    def initialize_permissions():
        permissions_data = {
            'Navigation': [
                ('NAV_DASHBOARD', 'Access to Dashboard'),
                ('NAV_USERS', 'Access to Users Management'),
                ('NAV_BRANCHES', 'Access to Branches Management'),
                ('NAV_ROLES', 'Access to Roles Management'),
                ('NAV_ZAPRIMANJE', 'Access to Zaprimanje Management'),
                ('NAV_REPORTS', 'Access to Reports')
            ],
            'Dashboard': [
                ('VIEW_USERS_STATS', 'Can view users statistics'),
                ('VIEW_BRANCHES_STATS', 'Can view branches statistics'),
                ('VIEW_ORDERS_STATS', 'Can view orders statistics'),
                ('VIEW_DELIVERY_STATS', 'Can view delivery statistics'),
                ('VIEW_CONNECTED_USERS', 'Can view connected users')
            ],
            'Management': [
                ('MANAGE_USERS', 'Can manage users'),
                ('MANAGE_BRANCHES', 'Can manage branches'),
                ('MANAGE_ROLES', 'Can manage roles'),
                ('MANAGE_PERMISSIONS', 'Can manage permissions')
            ],
            'Actions': [
                ('CREATE_USER', 'Can create users'),
                ('EDIT_USER', 'Can edit users'),
                ('DELETE_USER', 'Can delete users'),
                ('CREATE_BRANCH', 'Can create branches'),
                ('EDIT_BRANCH', 'Can edit branches'),
                ('DELETE_BRANCH', 'Can delete branches')
            ],
            'Zaprimanje': [
                ('ZAPRIMANJE_CREATE', 'Can create zaprimanje'),
                ('ZAPRIMANJE_EDIT', 'Can edit zaprimanje'),
                ('ZAPRIMANJE_DELETE', 'Can delete zaprimanje'),
                ('ZAPRIMANJE_COMPLETE', 'Can complete zaprimanje'),
                ('ZAPRIMANJE_VIEW', 'Can view zaprimanje')
            ]
        }
        for category, perms in permissions_data.items():
            for perm_name, desc in perms:
                if not Permission.query.filter_by(permission_name=perm_name).first():
                    permission = Permission(permission_name=perm_name, description=desc)
                    db.session.add(permission)
        
        db.session.commit()

    @staticmethod
    def get_permissions_by_category():
        permissions = Permission.query.all()
        return {
            'navigation': [p for p in permissions if p.permission_name.startswith('NAV_')],
            'dashboard': [p for p in permissions if p.permission_name.startswith('VIEW_')],
            'management': [p for p in permissions if p.permission_name.startswith('MANAGE_')],
            'actions': [p for p in permissions if p.permission_name in ['CREATE_', 'EDIT_', 'DELETE_']],
            'zaprimanje': [p for p in permissions if p.permission_name.startswith('ZAPRIMANJE_')]
        }
      
   