from flask_login import UserMixin
from app.extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.role import Role
from app.models.permission import Permission  # Use explicit import

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    full_name = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    last_login = db.Column(db.DateTime)
    role = db.relationship('Role', backref='users')
    branch = db.relationship('Branch', backref='users')

    def set_password(self, password):
        # Force using pbkdf2:sha256 method with 600000 iterations
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    
    def check_password(self, password):
        if self.password_hash.startswith('pbkdf2:sha256:'):
            return check_password_hash(self.password_hash, password)
        else:
            return self.password_hash == password

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def is_admin(self):
        return self.role.role_name == 'Admin' if self.role else False

    def has_permission(self, permission):
        return self.role and self.role.role_name == 'Admin'

    def get_branch_code(self):
        return self.branch.branch_code if self.branch else None
    
    def has_permission(self, permission_name):
        if self.role and self.role.role_name == 'Admin':
            return True  # Admin has all permissions
        if self.role:
            return any(p.permission_name == permission_name for p in self.role.permissions)
        return False        
        return False