from app import db
from datetime import datetime

class SSCCZaprimljeno(db.Model):
    __tablename__ = 'SSCC_zaprimljeno'
    
    id = db.Column(db.Integer, primary_key=True)
    incoming_goods_id = db.Column(db.Integer, db.ForeignKey('incoming_goods.id'))
    delivery_note = db.Column(db.String(50))
    sscc = db.Column(db.String(50))
    PSSCC = db.Column(db.String(50))
    document_msi = db.Column(db.String(50))
    barcode = db.Column(db.String(50))
    item_code = db.Column(db.String(50))
    description = db.Column(db.Text)
    uom = db.Column(db.String(20))
    quantity = db.Column(db.Numeric(18, 2))
    received_qty = db.Column(db.Numeric(18, 2))
    difference = db.Column(db.Numeric(18, 2))
    status_text = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_received = db.Column(db.String(100))

