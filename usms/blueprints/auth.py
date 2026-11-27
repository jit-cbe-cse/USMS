from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..access import record_activity
from ..extensions import db
from ..models import User

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and user.active and user.check_password(request.form.get("password") or ""):
            login_user(user, remember=bool(request.form.get("remember")))
            record_activity("login", user=user)
            db.session.commit()
            return redirect(url_for("index"))
        flash("Invalid email or password.", "error")
    return render_template("auth/login.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    record_activity("logout")
    db.session.commit()
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        new = request.form.get("new_password") or ""
        if not current_user.check_password(request.form.get("current_password") or ""):
            flash("Current password is incorrect.", "error")
        elif len(new) < 8:
            flash("New password must be at least 8 characters.", "error")
        else:
            current_user.set_password(new)
            record_activity("change_password")
            db.session.commit()
            flash("Password updated.", "success")
            return redirect(url_for("index"))
    return render_template("auth/password.html")
