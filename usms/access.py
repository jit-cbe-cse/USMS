"""Role-based access helpers. All permission rules live here."""
from functools import wraps

from flask import abort, request
from flask_login import current_user, login_required

from .extensions import db
from .models import ActivityLog, Internship, Role, User


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def visible_students_query(user):
    """Students a user may see: admin/professor = all, HR = interns of their company."""
    q = User.query.filter(User.role == Role.STUDENT)
    if user.role in (Role.ADMIN, Role.PROFESSOR):
        return q
    if user.role == Role.HR and user.company_id:
        return q.join(Internship, Internship.student_id == User.id).filter(
            Internship.company_id == user.company_id).distinct()
    return q.filter(User.id == user.id) if user.role == Role.STUDENT else q.filter(False)


def visible_internships_query(user):
    q = Internship.query
    if user.role in (Role.ADMIN, Role.PROFESSOR):
        return q
    if user.role == Role.HR:
        return q.filter(Internship.company_id == (user.company_id or -1))
    return q.filter(Internship.student_id == user.id)


def can_view_internship(user, internship):
    if user.role in (Role.ADMIN, Role.PROFESSOR):
        return True
    if user.role == Role.HR:
        return internship.company_id == user.company_id
    return internship.student_id == user.id


def can_manage_internship(user, internship):
    """Approve leave, edit internship etc. Professors can view but HR runs the company side."""
    if user.role == Role.ADMIN:
        return True
    return user.role == Role.HR and internship.company_id == user.company_id


def record_activity(action, details=None, user=None):
    user = user or (current_user if current_user.is_authenticated else None)
    db.session.add(ActivityLog(
        user_id=user.id if user else None, action=action, details=(details or "")[:500],
        ip_address=request.remote_addr if request else None,
    ))
