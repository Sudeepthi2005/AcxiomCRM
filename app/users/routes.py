from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..extensions import db
from ..models import User, Role
from ..utils import roles_required, audit

users_bp=Blueprint("users",__name__,url_prefix="/users")

@users_bp.route("/")
@login_required
@roles_required("Admin")
def index():
    return render_template("users/index.html", users=User.query.order_by(User.id.desc()).all())

@users_bp.route("/create",methods=["GET","POST"])
@login_required
@roles_required("Admin")
def create():
    roles=Role.query.all()
    if request.method=="POST":
        name=request.form.get("name","").strip(); email=request.form.get("email","").strip().lower(); password=request.form.get("password","")
        if not name or not email or len(password)<8: flash("Name, email and password (8+ chars) are required.","danger")
        elif User.query.filter_by(email=email).first(): flash("Email already exists.","danger")
        else:
            u=User(name=name,email=email,role_id=int(request.form.get("role_id")),is_active=True); u.set_password(password)
            db.session.add(u); db.session.commit(); audit("CREATE","User",u.id)
            flash("User created.","success"); return redirect(url_for("users.index"))
    return render_template("users/form.html", user=None, roles=roles)

@users_bp.route("/<int:id>/toggle",methods=["POST"])
@login_required
@roles_required("Admin")
def toggle(id):
    u=User.query.get_or_404(id); u.is_active=not u.is_active
    db.session.commit(); audit("STATUS_CHANGE","User",u.id); return redirect(url_for("users.index"))
