from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..access import record_activity, roles_required
from ..extensions import db
from ..forms import FormError, optional, required
from ..models import ActivityLog, Company, Internship, LeaveRequest, LeaveStatus, LogEntry, Role, User

bp = Blueprint("admin", __name__)


@bp.route("/")
@roles_required(Role.ADMIN)
def dashboard():
    stats = {
        "Companies": Company.query.count(),
        "Students": User.query.filter_by(role=Role.STUDENT).count(),
        "Professors": User.query.filter_by(role=Role.PROFESSOR).count(),
        "HR/Managers": User.query.filter_by(role=Role.HR).count(),
        "Internships": Internship.query.count(),
        "Logs": LogEntry.query.count(),
        "Pending leaves": LeaveRequest.query.filter_by(status=LeaveStatus.PENDING).count(),
    }
    recent = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


@bp.route("/companies", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def companies():
    if request.method == "POST":
        try:
            name = required(request.form, "name")
            if Company.query.filter_by(name=name).first():
                raise FormError("A company with that name already exists.")
            company = Company(name=name, website=optional(request.form, "website"),
                              address=optional(request.form, "address"))
            db.session.add(company)
            record_activity("create_company", name)
            db.session.commit()
            flash(f"Company {name} added.", "success")
            return redirect(url_for("admin.companies"))
        except FormError as e:
            flash(str(e), "error")
    return render_template("admin/companies.html", companies=Company.query.order_by(Company.name).all())


@bp.route("/users", methods=["GET", "POST"])
@roles_required(Role.ADMIN)
def users():
    if request.method == "POST":
        try:
            role = required(request.form, "role")
            if role not in Role.ALL:
                raise FormError("Invalid role.")
            email = required(request.form, "email").lower()
            if User.query.filter_by(email=email).first():
                raise FormError("A user with that email already exists.")
            password = required(request.form, "password")
            if len(password) < 8:
                raise FormError("Password must be at least 8 characters.")
            user = User(name=required(request.form, "name"), email=email, role=role,
                        roll_number=optional(request.form, "roll_number") if role == Role.STUDENT else None)
            if role == Role.HR:
                company_id = required(request.form, "company_id", "Company")
                user.company = db.get_or_404(Company, int(company_id))
            user.set_password(password)
            db.session.add(user)
            record_activity("create_user", f"{role}: {email}")
            db.session.commit()
            flash(f"{user.role_label} {email} added.", "success")
            return redirect(url_for("admin.users"))
        except FormError as e:
            flash(str(e), "error")
    role_filter = request.args.get("role")
    q = User.query.order_by(User.role, User.name)
    if role_filter in Role.ALL:
        q = q.filter_by(role=role_filter)
    return render_template("admin/users.html", users=q.all(), role_filter=role_filter,
                           companies=Company.query.order_by(Company.name).all())


@bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@roles_required(Role.ADMIN)
def toggle_user(user_id):
    user = db.get_or_404(User, user_id)
    user.active = not user.active
    record_activity("toggle_user", f"{user.email} active={user.active}")
    db.session.commit()
    flash(f"{user.email} is now {'active' if user.active else 'disabled'}.", "success")
    return redirect(url_for("admin.users"))


@bp.route("/activity")
@roles_required(Role.ADMIN)
def activity():
    page = request.args.get("page", 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).paginate(page=page, per_page=50)
    return render_template("admin/activity.html", logs=logs)
