from datetime import date, timedelta

import click

from .extensions import db
from .models import Attendance, Company, Internship, LeaveRequest, LogEntry, Role, User


def register_cli(app):
    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--name", prompt=True, default="Administrator")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(email, name, password):
        """Create (or reset) an admin account."""
        user = User.query.filter_by(email=email.lower()).first() or User(email=email.lower())
        user.name, user.role, user.active = name, Role.ADMIN, True
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Admin {email} ready.")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Load demo data (dev only). Every demo password is 'password'."""
        if User.query.first():
            click.echo("Database is not empty; skipping demo seed.")
            return
        acme = Company(name="Acme Labs", website="https://acme.example")
        globex = Company(name="Globex Corp", website="https://globex.example")
        db.session.add_all([acme, globex])

        def mk(name, email, role, **kw):
            u = User(name=name, email=email, role=role, **kw)
            u.set_password("password")
            db.session.add(u)
            return u

        mk("Admin", "admin@usms.local", Role.ADMIN)
        prof = mk("Prof. Rao", "prof@usms.local", Role.PROFESSOR)
        mk("Hannah (Acme HR)", "hr@acme.example", Role.HR, company=acme)
        mk("Gary (Globex HR)", "hr@globex.example", Role.HR, company=globex)
        s1 = mk("Asha Student", "asha@student.local", Role.STUDENT, roll_number="CS2023001")
        s2 = mk("Ben Student", "ben@student.local", Role.STUDENT, roll_number="CS2023002")

        today = date.today()
        past = Internship(student=s1, company=globex, title="Summer Intern",
                          start_date=today - timedelta(days=300), end_date=today - timedelta(days=240), added_by=prof)
        cur1 = Internship(student=s1, company=acme, title="Backend Intern",
                          start_date=today - timedelta(days=30), end_date=today + timedelta(days=60), added_by=prof)
        cur2 = Internship(student=s2, company=globex, title="Data Intern",
                          start_date=today - timedelta(days=10), added_by=prof)
        db.session.add_all([past, cur1, cur2])
        db.session.add(LogEntry(internship=cur1, log_date=today - timedelta(days=1),
                                title="Set up dev environment", body="Cloned repos, ran the test suite, met the team."))
        db.session.add(LeaveRequest(internship=cur1, start_date=today + timedelta(days=5),
                                    end_date=today + timedelta(days=6), reason="College exam"))
        for d in range(1, 6):
            db.session.add(Attendance(internship=cur1, day=today - timedelta(days=d)))
        db.session.commit()
        click.echo("Demo data loaded. Log in with e.g. admin@usms.local / password")
