from datetime import datetime
from ..extensions import db

class Lead(db.Model):
    __tablename__ = "leads"
    id = db.Column(db.Integer, primary_key=True)
    lead_code = db.Column(db.String(30), unique=True, nullable=False)
    lead_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    company_name = db.Column(db.String(120))
    source = db.Column(db.String(60), default="Website")
    status = db.Column(db.String(30), default="New")
    priority = db.Column(db.String(20), default="Medium")
    expected_value = db.Column(db.Float, default=0)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
