from app.extensions import db
from datetime import datetime

class IncomingGoodsCompleted(db.Model):
    __tablename__ = 'incoming_goods_completed'
    
    id = db.Column(db.Integer, primary_key=True)
    delivery_note = db.Column(db.String(50))
    sscc = db.Column(db.String(50))
    document_msi = db.Column(db.String(50))
    barcode = db.Column(db.String(50))
    item_code = db.Column(db.String(50))
    description = db.Column(db.Text)
    uom = db.Column(db.String(20))
    quantity = db.Column(db.Numeric(18, 2))
    received_qty = db.Column(db.Numeric(18, 2))
    receiver = db.Column(db.String(100))
    user_received = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    poslovnica = db.Column('Poslovnica', db.String(2))
    @property
    def difference(self):
        return float(self.received_qty or 0) - float(self.quantity or 0)

    @property
    def status(self):
        if self.received_qty == self.quantity:
            return 'Zaprimljeno'
        elif self.received_qty > self.quantity:
            return 'Višak'
        else:
            return 'Manjak'