from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from ..extensions import db
from ..models import Customer, Lead, Opportunity, FollowUp

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@login_required
def index():
    role = current_user.role_name
    if role == "Admin" or role == "Manager":
        customers = Customer.query.count()
        leads = Lead.query.count()
        opportunities = Opportunity.query.count()
        open_opportunities = Opportunity.query.filter_by(status="Open").count()
        won = Opportunity.query.filter_by(status="Won").count()
        lost = Opportunity.query.filter_by(status="Lost").count()
        pipeline = db.session.query(func.coalesce(func.sum(Opportunity.amount), 0)).filter_by(status="Open").scalar()
        lead_status = db.session.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
        opp_stage = db.session.query(Opportunity.stage, func.count(Opportunity.id)).group_by(Opportunity.stage).all()
    else:
        customers = Customer.query.filter_by(created_by=current_user.id).count()
        leads = Lead.query.filter_by(assigned_to=current_user.id).count()
        opportunities = Opportunity.query.filter_by(assigned_to=current_user.id).count()
        open_opportunities = Opportunity.query.filter_by(assigned_to=current_user.id, status="Open").count()
        won = Opportunity.query.filter_by(assigned_to=current_user.id, status="Won").count()
        lost = Opportunity.query.filter_by(assigned_to=current_user.id, status="Lost").count()
        pipeline = db.session.query(func.coalesce(func.sum(Opportunity.amount), 0)).filter_by(assigned_to=current_user.id, status="Open").scalar()
        lead_status = db.session.query(Lead.status, func.count(Lead.id)).filter_by(assigned_to=current_user.id).group_by(Lead.status).all()
        opp_stage = db.session.query(Opportunity.stage, func.count(Opportunity.id)).filter_by(assigned_to=current_user.id).group_by(Opportunity.stage).all()
    followups = FollowUp.query.filter_by(assigned_to=current_user.id, status="Planned").count()
    return render_template("dashboard/index.html",
        customers=customers, leads=leads, opportunities=opportunities,
        open_opportunities=open_opportunities, won=won, lost=lost,
        pipeline=float(pipeline or 0), followups=followups,
        lead_labels=[x[0] for x in lead_status], lead_values=[x[1] for x in lead_status],
        stage_labels=[x[0] for x in opp_stage], stage_values=[x[1] for x in opp_stage])
