from datetime import date
from functools import wraps
from flask import abort, request
from flask_login import current_user
from .extensions import db
from .models import AuditLog

def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role_name not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator

def audit(action, entity_name=None, record_id=None, old_value=None, new_value=None):
    entry = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        entity_name=entity_name,
        record_id=str(record_id) if record_id is not None else None,
        old_value=old_value,
        new_value=new_value,
        ip_address=request.remote_addr
    )
    db.session.add(entry)
    db.session.commit()
