from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Customer
from ..utils import audit, roles_required
import re

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

def valid_phone(phone):
    return bool(re.fullmatch(r"[6-9][0-9]{9}", phone or ""))

@customers_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    query = Customer.query
    if current_user.role_name == "Sales Executive":
        query = query.filter_by(created_by=current_user.id)
    if q:
        like = f"%{q}%"
        query = query.filter((Customer.customer_name.ilike(like)) | (Customer.email.ilike(like)) | (Customer.phone.ilike(like)) | (Customer.company_name.ilike(like)))
    customers = query.order_by(Customer.id.desc()).all()
    return render_template("customers/index.html", customers=customers, q=q)

@customers_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        name = request.form.get("customer_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        if not name or len(name) > 120:
            flash("Customer name is required.", "danger")
        elif not email or "@" not in email:
            flash("Enter a valid email address.", "danger")
        elif not valid_phone(phone):
            flash("Enter a valid 10-digit Indian mobile number.", "danger")
        elif Customer.query.filter((Customer.email == email) | (Customer.phone == phone)).first():
            flash("Customer with the same email or phone already exists.", "danger")
        else:
            c = Customer(
                customer_code=f"CUST-{Customer.query.count()+1:04d}",
                customer_name=name, email=email, phone=phone,
                company_name=request.form.get("company_name"),
                address=request.form.get("address"), city=request.form.get("city"),
                state=request.form.get("state"), status=request.form.get("status","Active"),
                created_by=current_user.id
            )
            db.session.add(c)
            db.session.commit()
            audit("CREATE", "Customer", c.id)
            flash("Customer created successfully.", "success")
            return redirect(url_for("customers.index"))
    return render_template("customers/form.html", customer=None)

@customers_bp.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit(id):
    c = Customer.query.get_or_404(id)
    if current_user.role_name == "Sales Executive" and c.created_by != current_user.id:
        return "Forbidden", 403
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        phone = request.form.get("phone","").strip()
        duplicate = Customer.query.filter(Customer.id != c.id, ((Customer.email == email) | (Customer.phone == phone))).first()
        if not request.form.get("customer_name","").strip():
            flash("Customer name is required.", "danger")
        elif "@" not in email:
            flash("Enter a valid email address.", "danger")
        elif not valid_phone(phone):
            flash("Enter a valid phone number.", "danger")
        elif duplicate:
            flash("Email or phone already belongs to another customer.", "danger")
        else:
            c.customer_name=request.form.get("customer_name").strip()
            c.email=email; c.phone=phone; c.company_name=request.form.get("company_name")
            c.address=request.form.get("address"); c.city=request.form.get("city")
            c.state=request.form.get("state"); c.status=request.form.get("status","Active")
            db.session.commit()
            audit("UPDATE", "Customer", c.id)
            flash("Customer updated.", "success")
            return redirect(url_for("customers.index"))
    return render_template("customers/form.html", customer=c)

@customers_bp.route("/<int:id>/delete", methods=["POST"])
@login_required
def delete(id):
    c = Customer.query.get_or_404(id)
    if current_user.role_name != "Admin":
        return "Forbidden", 403
    c.status = "Inactive"
    db.session.commit()
    audit("DELETE", "Customer", c.id)
    flash("Customer deactivated.", "success")
    return redirect(url_for("customers.index"))
