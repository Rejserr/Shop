from app.extensions import db
from datetime import datetime
from app.models.user import User

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    logout_time = db.Column(db.DateTime)
    ip_address = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')
    device_type = db.Column(db.String(20))
    
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))

    @classmethod
    def get_active_sessions(cls, branch_id=None):
        query = cls.query.filter_by(status='active', logout_time=None)
        if branch_id:
            query = query.join(User).filter(User.branch_id == branch_id)
        return query.all()

    @classmethod
    def close_active_sessions(cls, user_id, device_type):
        """Close all active sessions for a user on a specific device type"""
        active_sessions = cls.query.filter_by(
            user_id=user_id,
            device_type=device_type,
            status='active',
            logout_time=None
        ).all()
        
        for session in active_sessions:
            session.status = 'completed'
            session.logout_time = datetime.now()
        
        db.session.commit()
        return len(active_sessions)