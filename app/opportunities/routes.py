from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Opportunity, Customer, User
from ..utils import audit

opportunities_bp=Blueprint("opportunities",__name__,url_prefix="/opportunities")
STAGES=["Qualification","Proposal","Negotiation","Won","Lost"]

@opportunities_bp.route("/")
@login_required
def index():
    query=Opportunity.query
    if current_user.role_name=="Sales Executive":
        query=query.filter_by(assigned_to=current_user.id)
    q=request.args.get("q","").strip()
    if q: query=query.filter(Opportunity.opportunity_name.ilike(f"%{q}%"))
    return render_template("opportunities/index.html", opportunities=query.order_by(Opportunity.id.desc()).all(), q=q)

@opportunities_bp.route("/create",methods=["GET","POST"])
@login_required
def create():
    customers=Customer.query.all()
    users=User.query.filter_by(is_active=True).all()
    if request.method=="POST":
        name=request.form.get("opportunity_name","").strip()
        amount=float(request.form.get("amount") or 0)
        probability=int(request.form.get("probability") or 0)
        close=request.form.get("expected_close_date")
        stage=request.form.get("stage","Qualification")
        if not name: flash("Opportunity name is required.","danger")
        elif amount<=0: flash("Opportunity Amount must be greater than 0.","danger")
        elif not 0<=probability<=100: flash("Probability must be between 0 and 100.","danger")
        elif not close or date.fromisoformat(close)<date.today(): flash("Expected Close Date cannot be in the past.","danger")
        elif stage not in STAGES: flash("Invalid opportunity stage.","danger")
        else:
            o=Opportunity(opportunity_name=name,customer_id=int(request.form.get("customer_id")) if request.form.get("customer_id") else None,
                amount=amount,probability=probability,expected_close_date=date.fromisoformat(close),
                stage=stage,status="Won" if stage=="Won" else "Lost" if stage=="Lost" else "Open",
                assigned_to=int(request.form.get("assigned_to") or current_user.id),notes=request.form.get("notes"))
            db.session.add(o); db.session.commit(); audit("CREATE","Opportunity",o.id)
            flash("Opportunity created.","success"); return redirect(url_for("opportunities.index"))
    return render_template("opportunities/form.html", opportunity=None, customers=customers, users=users, stages=STAGES)

@opportunities_bp.route("/<int:id>/edit",methods=["GET","POST"])
@login_required
def edit(id):
    o=Opportunity.query.get_or_404(id)
    if current_user.role_name=="Sales Executive" and o.assigned_to != current_user.id: return "Forbidden",403
    customers=Customer.query.all(); users=User.query.filter_by(is_active=True).all()
    if request.method=="POST":
        amount=float(request.form.get("amount") or 0); probability=int(request.form.get("probability") or 0)
        close=date.fromisoformat(request.form.get("expected_close_date"))
        stage=request.form.get("stage")
        if amount<=0: flash("Opportunity Amount must be greater than 0.","danger")
        elif not 0<=probability<=100: flash("Probability must be between 0 and 100.","danger")
        elif close<date.today() and stage not in ["Won","Lost"]: flash("Expected Close Date cannot be in the past.","danger")
        else:
            o.opportunity_name=request.form.get("opportunity_name","").strip()
            o.customer_id=int(request.form.get("customer_id")) if request.form.get("customer_id") else None
            o.amount=amount; o.probability=probability; o.expected_close_date=close
            o.stage=stage; o.status="Won" if stage=="Won" else "Lost" if stage=="Lost" else "Open"
            o.notes=request.form.get("notes")
            if current_user.role_name!="Sales Executive": o.assigned_to=int(request.form.get("assigned_to") or current_user.id)
            db.session.commit(); audit("UPDATE","Opportunity",o.id)
            flash("Opportunity updated.","success"); return redirect(url_for("opportunities.index"))
    return render_template("opportunities/form.html", opportunity=o, customers=customers, users=users, stages=STAGES)
