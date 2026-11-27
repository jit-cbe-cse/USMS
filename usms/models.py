from datetime import date, datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Role:
    ADMIN = "admin"
    PROFESSOR = "professor"
    HR = "hr"
    STUDENT = "student"
    ALL = (ADMIN, PROFESSOR, HR, STUDENT)
    LABELS = {ADMIN: "Admin", PROFESSOR: "Professor", HR: "Company HR/Manager", STUDENT: "Student"}


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    website = db.Column(db.String(255))
    address = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    staff = db.relationship("User", back_populates="company")
    internships = db.relationship("Internship", back_populates="company")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)
    # Students: roll / registration number. HR: company they belong to.
    roll_number = db.Column(db.String(50), unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    company = db.relationship("Company", back_populates="staff")
    internships = db.relationship(
        "Internship", back_populates="student", foreign_keys="Internship.student_id",
        order_by="Internship.start_date.desc()",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.active

    @property
    def role_label(self):
        return Role.LABELS.get(self.role, self.role)

    @property
    def current_internship(self):
        for i in self.internships:
            if i.is_current:
                return i
        return None


class Internship(db.Model):
    """One stint of a student at a company. A student's history is all of these."""
    __tablename__ = "internships"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, default="Intern")
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)  # null = ongoing / open-ended
    added_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    student = db.relationship("User", back_populates="internships", foreign_keys=[student_id])
    company = db.relationship("Company", back_populates="internships")
    added_by = db.relationship("User", foreign_keys=[added_by_id])
    logs = db.relationship("LogEntry", back_populates="internship", order_by="LogEntry.log_date.desc()",
                           cascade="all, delete-orphan")
    leave_requests = db.relationship("LeaveRequest", back_populates="internship",
                                     order_by="LeaveRequest.created_at.desc()", cascade="all, delete-orphan")
    attendance = db.relationship("Attendance", back_populates="internship",
                                 order_by="Attendance.day.desc()", cascade="all, delete-orphan")

    @property
    def is_current(self):
        today = date.today()
        return self.start_date <= today and (self.end_date is None or self.end_date >= today)

    @property
    def status(self):
        today = date.today()
        if self.start_date > today:
            return "upcoming"
        return "current" if self.is_current else "completed"

    @property
    def duration_days(self):
        end = self.end_date or date.today()
        return max((end - self.start_date).days + 1, 0)


class LogEntry(db.Model):
    """A student's work log / note for a day."""
    __tablename__ = "log_entries"
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey("internships.id"), nullable=False, index=True)
    log_date = db.Column(db.Date, nullable=False, default=date.today)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    internship = db.relationship("Internship", back_populates="logs")


class LeaveStatus:
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class LeaveRequest(db.Model):
    __tablename__ = "leave_requests"
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey("internships.id"), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=LeaveStatus.PENDING, index=True)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    reviewed_at = db.Column(db.DateTime)
    review_note = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)

    internship = db.relationship("Internship", back_populates="leave_requests")
    reviewed_by = db.relationship("User")

    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1


class Attendance(db.Model):
    __tablename__ = "attendance"
    __table_args__ = (db.UniqueConstraint("internship_id", "day", name="uq_attendance_internship_day"),)
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey("internships.id"), nullable=False, index=True)
    day = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default="present")  # present / absent / leave
    check_in_at = db.Column(db.DateTime, default=utcnow)

    internship = db.relationship("Internship", back_populates="attendance")


class ActivityLog(db.Model):
    """Audit trail of user actions, visible to admins."""
    __tablename__ = "activity_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(500))
    ip_address = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)

    user = db.relationship("User")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
