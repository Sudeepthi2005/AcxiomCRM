from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Lead, User, Customer, Opportunity
from ..utils import audit

leads_bp = Blueprint("leads", __name__, url_prefix="/leads")
STATUSES = ["New","Contacted","Qualified","Unqualified","Converted","Lost"]

@leads_bp.route("/")
@login_required
def index():
    q=request.args.get("q","").strip()
    query=Lead.query
    if current_user.role_name=="Sales Executive":
        query=query.filter_by(assigned_to=current_user.id)
    if q:
        query=query.filter(Lead.lead_name.ilike(f"%{q}%"))
    return render_template("leads/index.html", leads=query.order_by(Lead.id.desc()).all(), q=q)

@leads_bp.route("/create", methods=["GET","POST"])
@login_required
def create():
    users=User.query.filter_by(is_active=True).all()
    if request.method=="POST":
        name=request.form.get("lead_name","").strip()
        expected=float(request.form.get("expected_value") or 0)
        status=request.form.get("status","New")
        if not name:
            flash("Lead name is required.","danger")
        elif status not in STATUSES:
            flash("Invalid lead status.","danger")
        elif expected < 0:
            flash("Expected value cannot be negative.","danger")
        else:
            l=Lead(lead_code=f"LEAD-{Lead.query.count()+1:04d}", lead_name=name,
                email=request.form.get("email"), phone=request.form.get("phone"),
                company_name=request.form.get("company_name"), source=request.form.get("source"),
                status=status, priority=request.form.get("priority","Medium"),
                expected_value=expected, assigned_to=int(request.form.get("assigned_to") or current_user.id))
            db.session.add(l); db.session.commit(); audit("CREATE","Lead",l.id)
            flash("Lead created.","success"); return redirect(url_for("leads.index"))
    return render_template("leads/form.html", lead=None, users=users, statuses=STATUSES)

@leads_bp.route("/<int:id>/edit", methods=["GET","POST"])
@login_required
def edit(id):
    lead=Lead.query.get_or_404(id)
    if current_user.role_name=="Sales Executive" and lead.assigned_to != current_user.id:
        return "Forbidden",403
    users=User.query.filter_by(is_active=True).all()
    if request.method=="POST":
        status=request.form.get("status","New")
        expected=float(request.form.get("expected_value") or 0)
        if status not in STATUSES or expected<0:
            flash("Invalid lead status/value.","danger")
        else:
            lead.lead_name=request.form.get("lead_name","").strip()
            lead.email=request.form.get("email"); lead.phone=request.form.get("phone")
            lead.company_name=request.form.get("company_name"); lead.source=request.form.get("source")
            lead.status=status; lead.priority=request.form.get("priority")
            lead.expected_value=expected
            if current_user.role_name != "Sales Executive":
                lead.assigned_to=int(request.form.get("assigned_to") or current_user.id)
            db.session.commit(); audit("UPDATE","Lead",lead.id)
            flash("Lead updated.","success"); return redirect(url_for("leads.index"))
    return render_template("leads/form.html", lead=lead, users=users, statuses=STATUSES)
