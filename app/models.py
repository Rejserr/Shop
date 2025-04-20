from app import db

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    branch_code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    def __repr__(self):
        return f'<Branch {self.name}>'