from flask import Flask, redirect, render_template, url_for
from flask_login import current_user

from .config import Config
from .extensions import csrf, db, login_manager, migrate


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)

    import os
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db, directory=os.path.join(os.path.dirname(app.root_path), "migrations"))
    login_manager.init_app(app)
    csrf.init_app(app)

    from . import models  # noqa: F401  (register models for migrations)
    from .blueprints.admin import bp as admin_bp
    from .blueprints.auth import bp as auth_bp
    from .blueprints.staff import bp as staff_bp
    from .blueprints.student import bp as student_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(staff_bp, url_prefix="/staff")
    app.register_blueprint(student_bp, url_prefix="/me")

    from .cli import register_cli
    register_cli(app)

    from .models import Role

    @app.context_processor
    def inject_roles():
        return {"Role": Role}

    @app.route("/")
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role == Role.STUDENT:
            return redirect(url_for("student.dashboard"))
        if current_user.role == Role.ADMIN:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("staff.dashboard"))

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("error.html", code=403, message="You don't have access to this page."), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", code=404, message="Page not found."), 404

    return app
