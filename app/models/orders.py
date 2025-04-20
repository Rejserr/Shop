from app.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    status = db.Column(db.String(20))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
