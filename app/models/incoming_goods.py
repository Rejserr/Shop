from app.extensions import db
from datetime import datetime
from sqlalchemy import Numeric, Computed  

class IncomingGoods(db.Model):
    __tablename__ = 'incoming_goods'
    
    id = db.Column(db.Integer, primary_key=True)
    delivery_note = db.Column(db.String(50))
    sscc = db.Column(db.String(50))
    PSSCC = db.Column(db.String(50))
    sales_order = db.Column(db.String(50))
    document_msi = db.Column(db.String(50))
    barcode = db.Column(db.String(50))
    item_code = db.Column(db.String(50))
    description = db.Column(db.Text)
    uom = db.Column(db.String(20))
    quantity = db.Column(db.Numeric(18, 2))
    received_qty = db.Column(db.Numeric(18, 2), default=0)
    receiver = db.Column(db.String(100))
    customer = db.Column(db.String(100))
    delivery_type = db.Column(db.String(50))
    order_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_received = db.Column(db.String(100))
    poslovnica = db.Column('Poslovnica', db.String(2))
    @property
    def difference(self):
        return float(self.received_qty or 0) - float(self.quantity or 0)

    @property
    def status(self):
        if not self.received_qty:
            return 'Nije zaprimljeno'
        elif self.received_qty == self.quantity:
            return 'Zaprimljeno'
        else:
            return 'Zaprima se'        
        return "Zaprimljeno" if self.difference == 0 else "Manjak"


