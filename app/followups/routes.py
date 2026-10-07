from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import FollowUp, Customer, Lead, User
from ..utils import audit

followups_bp=Blueprint("followups",__name__,url_prefix="/followups")

@followups_bp.route("/")
@login_required
def index():
    query=FollowUp.query
    if current_user.role_name=="Sales Executive": query=query.filter_by(assigned_to=current_user.id)
    return render_template("followups/index.html", followups=query.order_by(FollowUp.follow_up_date).all())

@followups_bp.route("/create",methods=["GET","POST"])
@login_required
def create():
    customers=Customer.query.all(); leads=Lead.query.all(); users=User.query.filter_by(is_active=True).all()
    if request.method=="POST":
        d=date.fromisoformat(request.form.get("follow_up_date"))
        if d<date.today():
            flash("Follow-up date cannot be earlier than today.","danger")
        else:
            f=FollowUp(customer_id=int(request.form.get("customer_id")) if request.form.get("customer_id") else None,
                lead_id=int(request.form.get("lead_id")) if request.form.get("lead_id") else None,
                follow_up_date=d,follow_up_type=request.form.get("follow_up_type"),
                remarks=request.form.get("remarks"),status="Planned",
                assigned_to=int(request.form.get("assigned_to") or current_user.id))
            db.session.add(f); db.session.commit(); audit("CREATE","FollowUp",f.id)
            flash("Follow-up scheduled.","success"); return redirect(url_for("followups.index"))
    return render_template("followups/form.html", followup=None, customers=customers, leads=leads, users=users)

@followups_bp.route("/<int:id>/complete",methods=["POST"])
@login_required
def complete(id):
    f=FollowUp.query.get_or_404(id)
    if current_user.role_name=="Sales Executive" and f.assigned_to!=current_user.id: return "Forbidden",403
    f.status="Completed"; db.session.commit(); audit("COMPLETE","FollowUp",f.id)
    flash("Follow-up completed.","success"); return redirect(url_for("followups.index"))
