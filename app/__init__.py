from flask import Flask
from config import Config
from .extensions import db, login_manager, csrf

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    from .context import inject_globals
    app.context_processor(inject_globals)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"

    from .models import User, Role
    from .auth.routes import auth_bp
    from .dashboard.routes import dashboard_bp
    from .customers.routes import customers_bp
    from .leads.routes import leads_bp
    from .opportunities.routes import opportunities_bp
    from .followups.routes import followups_bp
    from .users.routes import users_bp
    from .audit.routes import audit_bp
    from .reports.routes import reports_bp
    from .api.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(opportunities_bp)
    app.register_blueprint(followups_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        seed_data()

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return db.session.get(User, int(user_id))

def seed_data():
    from .models import User, Role
    roles = ["Admin", "Manager", "Sales Executive"]
    for name in roles:
        if not Role.query.filter_by(name=name).first():
            db.session.add(Role(name=name))
    db.session.commit()

    admin_role = Role.query.filter_by(name="Admin").first()
    if not User.query.filter_by(email="svundavi2@gitam.in").first():
        user = User(
            name="System Admin",
            email="svundavi2@gitam.in",
            role_id=admin_role.id,
            is_active=True
        )
        user.set_password("abc123")
        db.session.add(user)
        db.session.commit()
