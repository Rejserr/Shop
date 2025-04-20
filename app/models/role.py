from app.extensions import db
from app.models.permission import Permission

# Define the association table
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'))
)

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))
    
    permissions = db.relationship('Permission', 
                                secondary='role_permissions',
                                backref=db.backref('roles', lazy='dynamic'))

    def set_permissions(self, permission_names):
        self.permissions = []
        permissions = Permission.query.filter(Permission.permission_name.in_(permission_names)).all()
        for permission in permissions:
            self.permissions.append(permission)

    def has_permission(self, permission_name):
        return any(p.permission_name == permission_name for p in self.permissions)