from datetime import date

from usms.extensions import db
from usms.models import Internship, LeaveRequest, LogEntry, User


def test_login_redirects_by_role(login):
    assert b"Admin dashboard" in login("admin@usms.local").data
    assert b"Current internship" in login("asha@student.local").data
    assert b"Current interns" in login("prof@usms.local").data


def test_bad_password_rejected(login):
    assert b"Invalid email or password" in login("admin@usms.local", "nope").data


def test_student_creates_log_and_professor_sees_it(client, login):
    login("asha@student.local")
    r = client.post("/me/logs/new", data={"title": "Wrote API", "body": "Did the endpoint",
                                          "log_date": date.today().isoformat()}, follow_redirects=True)
    assert b"Log saved" in r.data
    asha = User.query.filter_by(email="asha@student.local").first()
    login("prof@usms.local")
    assert b"Wrote API" in client.get(f"/staff/students/{asha.id}").data


def test_hr_only_sees_own_company_students(client, login):
    asha = User.query.filter_by(email="asha@student.local").first()  # current at Acme, past at Globex
    ben = User.query.filter_by(email="ben@student.local").first()    # Globex only
    login("hr@acme.example")
    assert client.get(f"/staff/students/{ben.id}").status_code == 404
    page = client.get(f"/staff/students/{asha.id}").data
    assert b"Acme Labs" in page and b"Globex" not in page


def test_student_cannot_access_staff_or_admin(client, login):
    login("asha@student.local")
    assert client.get("/staff/students").status_code == 403
    assert client.get("/admin/").status_code == 403


def test_student_cannot_edit_others_log(client, login):
    ben_internship = Internship.query.join(User, Internship.student_id == User.id) \
        .filter(User.email == "ben@student.local").first()
    from usms.extensions import db
    entry = LogEntry(internship=ben_internship, title="x", body="y")
    db.session.add(entry)
    db.session.commit()
    login("asha@student.local")
    assert client.get(f"/me/logs/{entry.id}/edit").status_code == 403


def test_hr_approves_leave_other_hr_cannot(client, login):
    leave = LeaveRequest.query.first()  # Asha @ Acme
    login("hr@globex.example")
    assert client.post(f"/staff/leaves/{leave.id}/approve").status_code == 403
    login("prof@usms.local")
    assert client.post(f"/staff/leaves/{leave.id}/approve").status_code == 403
    login("hr@acme.example")
    client.post(f"/staff/leaves/{leave.id}/approve")
    assert db.session.get(LeaveRequest, leave.id).status == "approved"


def test_student_checkin_once_per_day(client, login):
    login("ben@student.local")
    client.post("/me/checkin")
    r = client.post("/me/checkin", follow_redirects=True)
    assert b"Already checked in" in r.data


def test_hr_adds_student_to_own_company(client, login):
    login("hr@acme.example")
    r = client.post("/staff/students/new", data={
        "email": "new@student.local", "name": "New Kid", "password": "password123",
        "start_date": date.today().isoformat(), "company_id": "999"}, follow_redirects=True)
    assert b"saved" in r.data
    new = User.query.filter_by(email="new@student.local").first()
    assert new.current_internship.company.name == "Acme Labs"  # company_id ignored for HR


def test_admin_creates_company_and_activity_logged(client, login):
    login("admin@usms.local")
    client.post("/admin/companies", data={"name": "Initech"})
    assert b"create_company" in client.get("/admin/activity").data


def test_every_page_renders_for_its_role(client, login):
    asha = User.query.filter_by(email="asha@student.local").first()
    pages = {
        "admin@usms.local": ["/admin/", "/admin/companies", "/admin/users", "/admin/activity",
                             "/staff/students", f"/staff/students/{asha.id}", "/staff/leaves?status=all"],
        "prof@usms.local": ["/staff/", "/staff/students", "/staff/students/new", f"/staff/students/{asha.id}"],
        "hr@acme.example": ["/staff/", "/staff/students/new", "/staff/leaves", f"/staff/students/{asha.id}"],
        "asha@student.local": ["/me/", "/me/logs", "/me/logs/new", "/me/leave", "/me/history", "/password"],
    }
    for email, urls in pages.items():
        login(email)
        for url in urls:
            assert client.get(url).status_code == 200, (email, url)
