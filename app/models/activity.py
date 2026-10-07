from datetime import datetime
from ..extensions import db

class Activity(db.Model):
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(40), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    activity_date = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"))
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(30), default="Completed")
