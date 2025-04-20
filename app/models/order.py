from app.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_date = db.Column(db.Date, default=datetime.utcnow)
    
    branch = db.relationship('Branch', backref='orders')
