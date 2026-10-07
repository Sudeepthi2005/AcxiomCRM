from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from ..extensions import db
from ..models import Customer, Lead, Opportunity
from ..utils import roles_required

reports_bp=Blueprint("reports",__name__,url_prefix="/reports")

@reports_bp.route("/")
@login_required
@roles_required("Admin","Manager","Sales Executive")
def index():
    pipeline=db.session.query(Opportunity.stage,func.sum(Opportunity.amount)).group_by(Opportunity.stage).all()
    lead_report=db.session.query(Lead.status,func.count(Lead.id)).group_by(Lead.status).all()
    return render_template("reports/index.html", pipeline=pipeline, lead_report=lead_report,
        customers=Customer.query.count(), leads=Lead.query.count(), opportunities=Opportunity.query.count())
