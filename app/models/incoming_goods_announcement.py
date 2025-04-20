from app import db
from datetime import datetime

class IncomingGoodsAnnouncement(db.Model):
    __tablename__ = 'incoming_goods_announcement'
    
    id = db.Column(db.Integer, primary_key=True)
    delivery_note = db.Column(db.String(50))
    sscc = db.Column(db.String(50))
    sales_order = db.Column(db.String(50))
    document_msi = db.Column(db.String(50))
    item_code = db.Column(db.String(50))
    description = db.Column(db.Text)
    uom = db.Column(db.String(20))
    quantity = db.Column(db.Numeric(18, 2))
    receiver = db.Column(db.String(100))
    customer = db.Column(db.String(100))
    delivery_type = db.Column(db.String(50))
    order_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    barcode = db.Column(db.String(50))
    branch_code = db.Column(db.String(2))