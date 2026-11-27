"""Views shared by professors, company HR/managers and admins."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ..access import (can_manage_internship, record_activity, roles_required,
                      visible_internships_query, visible_students_query)
from ..extensions import db
from ..forms import FormError, optional, parse_date, required
from ..models import Company, Internship, LeaveRequest, LeaveStatus, LogEntry, Role, User, utcnow

bp = Blueprint("staff", __name__)
STAFF = (Role.ADMIN, Role.PROFESSOR, Role.HR)


@bp.route("/")
@roles_required(*STAFF)
def dashboard():
    internships = visible_internships_query(current_user).all()
    current = [i for i in internships if i.is_current]
    ids = [i.id for i in internships] or [-1]
    pending = (LeaveRequest.query.filter(LeaveRequest.internship_id.in_(ids),
                                         LeaveRequest.status == LeaveStatus.PENDING).count())
    recent_logs = (LogEntry.query.filter(LogEntry.internship_id.in_(ids))
                   .order_by(LogEntry.created_at.desc()).limit(10).all())
    return render_template("staff/dashboard.html", current=current, pending=pending, recent_logs=recent_logs)


@bp.route("/students")
@roles_required(*STAFF)
def students():
    q = visible_students_query(current_user)
    search = (request.args.get("q") or "").strip()
    if search:
        like = f"%{search}%"
        q = q.filter(db.or_(User.name.ilike(like), User.email.ilike(like), User.roll_number.ilike(like)))
    return render_template("staff/students.html", students=q.order_by(User.name).all(), search=search)


@bp.route("/students/<int:student_id>")
@roles_required(*STAFF)
def student_detail(student_id):
    student = visible_students_query(current_user).filter(User.id == student_id).first_or_404()
    internships = visible_internships_query(current_user).filter(Internship.student_id == student.id) \
        .order_by(Internship.start_date.desc()).all()
    return render_template("staff/student_detail.html", student=student, internships=internships)


@bp.route("/students/new", methods=["GET", "POST"])
@roles_required(*STAFF)
def add_student():
    """Create a student account (or reuse an existing one) and optionally start an internship.

    HR can only add students into their own company, so for HR the internship is mandatory.
    """
    companies = _assignable_companies()
    if request.method == "POST":
        try:
            email = required(request.form, "email").lower()
            student = User.query.filter_by(email=email).first()
            if student and student.role != Role.STUDENT:
                raise FormError("That email belongs to a non-student account.")
            if student is None:
                password = required(request.form, "password", "Initial password")
                if len(password) < 8:
                    raise FormError("Password must be at least 8 characters.")
                student = User(email=email, role=Role.STUDENT, name=required(request.form, "name"),
                               roll_number=optional(request.form, "roll_number"))
                student.set_password(password)
                db.session.add(student)
                record_activity("create_student", email)

            company_id = optional(request.form, "company_id")
            if current_user.role == Role.HR:
                company_id = str(current_user.company_id)
            if company_id:
                company = next((c for c in companies if str(c.id) == company_id), None)
                if company is None:
                    raise FormError("Invalid company.")
                start = parse_date(request.form, "start_date", "Start date")
                end = parse_date(request.form, "end_date", required_=False)
                if end and end < start:
                    raise FormError("End date must be on or after start date.")
                db.session.add(Internship(student=student, company=company, start_date=start, end_date=end,
                                          title=optional(request.form, "title") or "Intern",
                                          added_by=current_user))
                record_activity("create_internship", f"{email} @ {company.name}")
            db.session.commit()
            flash(f"Student {email} saved.", "success")
            return redirect(url_for("staff.student_detail", student_id=student.id))
        except FormError as e:
            db.session.rollback()
            flash(str(e), "error")
    return render_template("staff/student_form.html", companies=companies)


@bp.route("/internships/<int:internship_id>/end", methods=["POST"])
@roles_required(Role.ADMIN, Role.HR)
def end_internship(internship_id):
    internship = db.get_or_404(Internship, internship_id)
    if not can_manage_internship(current_user, internship):
        abort(403)
    internship.end_date = parse_date(request.form, "end_date", "End date")
    record_activity("end_internship", f"{internship.student.email} @ {internship.company.name}")
    db.session.commit()
    flash("Internship end date updated.", "success")
    return redirect(url_for("staff.student_detail", student_id=internship.student_id))


@bp.route("/leaves")
@roles_required(*STAFF)
def leaves():
    status = request.args.get("status", LeaveStatus.PENDING)
    ids = [i.id for i in visible_internships_query(current_user)] or [-1]
    q = LeaveRequest.query.filter(LeaveRequest.internship_id.in_(ids))
    if status != "all":
        q = q.filter(LeaveRequest.status == status)
    return render_template("staff/leaves.html", requests=q.order_by(LeaveRequest.created_at.desc()).all(),
                           status=status)


@bp.route("/leaves/<int:leave_id>/<decision>", methods=["POST"])
@roles_required(Role.ADMIN, Role.HR)
def review_leave(leave_id, decision):
    leave = db.get_or_404(LeaveRequest, leave_id)
    if not can_manage_internship(current_user, leave.internship):
        abort(403)
    if decision not in ("approve", "deny"):
        abort(404)
    leave.status = LeaveStatus.APPROVED if decision == "approve" else LeaveStatus.DENIED
    leave.reviewed_by, leave.reviewed_at = current_user, utcnow()
    leave.review_note = optional(request.form, "note")
    record_activity(f"leave_{leave.status}", f"#{leave.id} {leave.internship.student.email}")
    db.session.commit()
    flash(f"Leave {leave.status}.", "success")
    return redirect(request.referrer or url_for("staff.leaves"))


def _assignable_companies():
    if current_user.role == Role.HR:
        return [current_user.company] if current_user.company else []
    return Company.query.order_by(Company.name).all()
