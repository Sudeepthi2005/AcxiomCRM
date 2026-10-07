from datetime import datetime
from ..extensions import db

class FollowUp(db.Model):
    __tablename__ = "follow_ups"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"))
    follow_up_date = db.Column(db.Date, nullable=False)
    follow_up_type = db.Column(db.String(40), default="Call")
    remarks = db.Column(db.Text)
    status = db.Column(db.String(30), default="Planned")
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    customer = db.relationship("Customer")
    lead = db.relationship("Lead")
