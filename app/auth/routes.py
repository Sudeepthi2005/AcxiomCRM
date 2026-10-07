from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from ..extensions import db
from ..models import User, Role
from ..utils import audit

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not user.is_active:
            flash("Invalid credentials or inactive account.", "danger")
            audit("LOGIN_FAILED", "User", user.id if user else None)
            return render_template("auth/login.html")
        if user.lockout_end and user.lockout_end > datetime.utcnow():
            flash("Account temporarily locked. Try again later.", "danger")
            return render_template("auth/login.html")
        if not user.check_password(password):
            user.failed_login_count += 1
            if user.failed_login_count >= 5:
                user.lockout_end = datetime.utcnow() + timedelta(minutes=15)
                user.failed_login_count = 0
                db.session.commit()
                audit("ACCOUNT_LOCKED", "User", user.id)
                flash("Account locked for 15 minutes after repeated failures.", "danger")
            else:
                db.session.commit()
                audit("LOGIN_FAILED", "User", user.id)
                flash("Invalid credentials.", "danger")
            return render_template("auth/login.html")
        user.failed_login_count = 0
        user.lockout_end = None
        db.session.commit()
        login_user(user)
        audit("LOGIN_SUCCESS", "User", user.id)
        return redirect(url_for("dashboard.index"))
    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or len(name) > 100:
            flash("Name is required and must be under 100 characters.", "danger")
        elif len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
        else:
            role = Role.query.filter_by(name="Sales Executive").first()
            user = User(name=name, email=email, role_id=role.id, is_active=True)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            audit("REGISTER", "User", user.id)
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    audit("LOGOUT", "User", current_user.id)
    logout_user()
    return redirect(url_for("auth.login"))
