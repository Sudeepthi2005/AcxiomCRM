from datetime import datetime
from ..extensions import db

class Opportunity(db.Model):
    __tablename__ = "opportunities"
    id = db.Column(db.Integer, primary_key=True)
    opportunity_name = db.Column(db.String(150), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    lead_id = db.Column(db.Integer, db.ForeignKey("leads.id"))
    amount = db.Column(db.Float, nullable=False)
    stage = db.Column(db.String(40), default="Qualification")
    probability = db.Column(db.Integer, default=10)
    expected_close_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), default="Open")
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"))
    notes = db.Column(db.Text)

    customer = db.relationship("Customer")
    lead = db.relationship("Lead")

    @property
    def weighted_value(self):
        return self.amount * self.probability / 100
