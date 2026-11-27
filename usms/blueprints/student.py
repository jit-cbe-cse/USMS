from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ..access import record_activity, roles_required
from ..extensions import db
from ..forms import FormError, parse_date, required
from ..models import Attendance, Internship, LeaveRequest, LogEntry, Role

bp = Blueprint("student", __name__)


def _current_or_redirect():
    internship = current_user.current_internship
    if internship is None:
        flash("You don't have an active internship right now.", "info")
    return internship


@bp.route("/")
@roles_required(Role.STUDENT)
def dashboard():
    internship = current_user.current_internship
    checked_in = bool(internship and Attendance.query.filter_by(
        internship_id=internship.id, day=date.today()).first())
    return render_template("student/dashboard.html", internship=internship, checked_in=checked_in)


@bp.route("/history")
@roles_required(Role.STUDENT)
def history():
    return render_template("student/history.html", internships=current_user.internships)


@bp.route("/logs")
@roles_required(Role.STUDENT)
def logs():
    entries = (LogEntry.query.join(Internship).filter(Internship.student_id == current_user.id)
               .order_by(LogEntry.log_date.desc(), LogEntry.id.desc()).all())
    return render_template("student/logs.html", entries=entries)


@bp.route("/logs/new", methods=["GET", "POST"])
@bp.route("/logs/<int:log_id>/edit", methods=["GET", "POST"])
@roles_required(Role.STUDENT)
def edit_log(log_id=None):
    entry = None
    if log_id is not None:
        entry = db.get_or_404(LogEntry, log_id)
        if entry.internship.student_id != current_user.id:
            abort(403)
    elif not (internship := _current_or_redirect()):
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        try:
            title = required(request.form, "title")
            body = required(request.form, "body", "Notes")
            log_date = parse_date(request.form, "log_date", "Date")
            if log_date > date.today():
                raise FormError("Log date can't be in the future.")
            if entry is None:
                entry = LogEntry(internship=internship)
                db.session.add(entry)
            entry.title, entry.body, entry.log_date = title, body, log_date
            record_activity("save_log", title)
            db.session.commit()
            flash("Log saved.", "success")
            return redirect(url_for("student.logs"))
        except FormError as e:
            flash(str(e), "error")
    return render_template("student/log_form.html", entry=entry, today=date.today())


@bp.route("/checkin", methods=["POST"])
@roles_required(Role.STUDENT)
def check_in():
    internship = _current_or_redirect()
    if internship:
        if Attendance.query.filter_by(internship_id=internship.id, day=date.today()).first():
            flash("Already checked in today.", "info")
        else:
            db.session.add(Attendance(internship=internship, day=date.today()))
            record_activity("check_in", internship.company.name)
            db.session.commit()
            flash("Checked in for today.", "success")
    return redirect(url_for("student.dashboard"))


@bp.route("/leave", methods=["GET", "POST"])
@roles_required(Role.STUDENT)
def leave():
    if request.method == "POST":
        internship = _current_or_redirect()
        if not internship:
            return redirect(url_for("student.leave"))
        try:
            start = parse_date(request.form, "start_date", "Start date")
            end = parse_date(request.form, "end_date", "End date")
            if end < start:
                raise FormError("End date must be on or after start date.")
            db.session.add(LeaveRequest(internship=internship, start_date=start, end_date=end,
                                        reason=required(request.form, "reason")))
            record_activity("request_leave", f"{start} to {end}")
            db.session.commit()
            flash("Leave request submitted.", "success")
            return redirect(url_for("student.leave"))
        except FormError as e:
            flash(str(e), "error")
    requests_ = (LeaveRequest.query.join(Internship).filter(Internship.student_id == current_user.id)
                 .order_by(LeaveRequest.created_at.desc()).all())
    return render_template("student/leave.html", requests=requests_)
