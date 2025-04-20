from app.extensions import db

class MasterData(db.Model):
    __tablename__ = 'Master_data'

    barcode = db.Column(db.String(50), primary_key=True)
    item_code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    uom = db.Column(db.String(20))
    pack = db.Column(db.Numeric(18,2))
    kataloski_broj = db.Column(db.String(50))
    bundle = db.Column(db.String(50))

    __table_args__ = (
        db.Index('idx_item_code', 'item_code'),
    )
