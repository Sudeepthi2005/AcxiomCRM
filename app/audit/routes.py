from flask import Blueprint, render_template
from flask_login import login_required
from ..models import AuditLog
from ..utils import roles_required

audit_bp=Blueprint("audit",__name__,url_prefix="/audit")

@audit_bp.route("/")
@login_required
@roles_required("Admin","Manager")
def index():
    return render_template("audit/index.html", logs=AuditLog.query.order_by(AuditLog.created_date.desc()).limit(500).all())
