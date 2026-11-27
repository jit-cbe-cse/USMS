# USMS: Unified Students Management System

An open-source system for colleges to manage student internships across many companies.
It keeps every student's full internship history (where they interned, for how long, and where they are now),
along with their daily work logs, attendance and leave requests.

Built with **Flask**, **SQLAlchemy**, and **Alembic** (via Flask-Migrate). It uses **SQLite** in development and **MySQL** in production.

## Roles

| Role | Can see | Can do (today) |
|---|---|---|
| **Admin** | Everything | Add companies and users (any role), enable or disable accounts, view user activity |
| **Professor** | All students and companies | Add students, assign internships, read logs, attendance and leave |
| **Company HR/Manager** | Interns of *their* company only | Add interns to their company, approve or deny leave, read logs and attendance, set internship end dates |
| **Student** | Only their own data | Write daily logs, check in for attendance, request leave, view internship history |

See [docs/ROADMAP.md](docs/ROADMAP.md) for what's planned next (certificates, document requests, Git integration, and more).

---

## Quick start (local development, SQLite)

Requirements: Python 3.11+ and git.

```bash
git clone https://github.com/jit-cbe-cse/USMS.git
cd USMS

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

cp .env.example .env                # create your local config (defaults use SQLite)

flask db upgrade                    # create the database from migrations
flask seed-demo                     # optional: demo companies, users, internships
flask run --port 5001               # http://127.0.0.1:5001
```

The SQLite file is created at `instance/usms.db`.

### Troubleshooting: port 5000 on macOS

AirPlay Receiver can occupy port 5000 on macOS. If Flask cannot bind to that
port, or the browser shows `403 Forbidden` instead of USMS, use port 5001 as
shown above. Alternatively, turn off AirPlay Receiver in System Settings
(search for "AirPlay Receiver"), then run Flask on its default port 5000.
This is only needed for local development.

### Demo accounts (after `flask seed-demo`)

Every demo account uses the password `password`.

| Email | Role |
|---|---|
| admin@usms.local | Admin |
| prof@usms.local | Professor |
| hr@acme.example | HR, Acme Labs |
| hr@globex.example | HR, Globex Corp |
| asha@student.local | Student (current at Acme, past at Globex) |
| ben@student.local | Student (current at Globex) |

To create a real admin instead: `flask create-admin`.

### Run tests

```bash
pytest
```

---

## Running with Docker (MySQL)

Requirements: Docker with the Compose plugin.

```bash
docker compose up --build -d            # starts MySQL 8 + USMS at http://localhost:8000
docker compose exec web flask create-admin
# or, for a demo: docker compose exec web flask seed-demo
```

The web container runs `flask db upgrade` on every start, so the schema stays current.
Compose reads `SECRET_KEY`, `MYSQL_PASSWORD` and `MYSQL_ROOT_PASSWORD` from your `.env` (see [Configuration](#configuration-env)). The defaults are for local testing only, so change them before deploying.

## Production without Docker (MySQL)

Set `SECRET_KEY` and `DATABASE_URL` either in `.env` or as exported variables:

```bash
# In MySQL:
#   CREATE DATABASE usms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
#   CREATE USER 'usms'@'%' IDENTIFIED BY 'strong-password';
#   GRANT ALL ON usms.* TO 'usms'@'%';

export SECRET_KEY="a-long-random-string"
export DATABASE_URL="mysql+pymysql://usms:strong-password@localhost:3306/usms?charset=utf8mb4"
pip install -r requirements.txt
flask db upgrade
flask create-admin
gunicorn -w 3 -b 0.0.0.0:8000 app:app
```

---

## Configuration (`.env`)

All configuration comes from environment variables. The easiest way to set them is a `.env` file in the project root:

```bash
cp .env.example .env
```

`.env.example` is the documented template and **is** committed. `.env` holds your real values and is git-ignored, so **never commit it**.
`flask` commands load `.env` automatically (via python-dotenv), and `docker compose` reads it for variable substitution.

| Variable | Default | Used by | Purpose |
|---|---|---|---|
| `FLASK_APP` | `app.py` | Flask CLI | App entry point |
| `FLASK_DEBUG` | unset | Flask CLI | `1` for auto-reload and debugger. **Dev only.** |
| `SECRET_KEY` | `dev-insecure-key` | App | Signs sessions. **Must** be a long random value in production: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | `sqlite:///usms.db` | App | Any SQLAlchemy URL. A relative SQLite path lives in `instance/`. MySQL: `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` |
| `MYSQL_PASSWORD` | `usms_password` | Docker Compose | Password for the `usms` MySQL user (the web container builds its `DATABASE_URL` from it) |
| `MYSQL_ROOT_PASSWORD` | `root_password` | Docker Compose | MySQL root password |

When you add a new setting, add it to `usms/config.py` **and** `.env.example` with a comment, and to the table above.

## Database migrations (Alembic)

Schema changes are versioned in `migrations/versions/`. **Never edit the database by hand.**

```bash
# 1. Change models in usms/models.py
flask db migrate -m "add documents table"   # 2. autogenerate a migration
# 3. Open the new file in migrations/versions/ and review it
flask db upgrade                             # 4. apply it
flask db downgrade                           # roll back one step if needed
```

Commit the migration file together with the model change. Batch mode is on, so `ALTER`s also work on SQLite.

## Project layout

```
.env.example            Config template (copy to .env)
app.py                  Entry point (flask run / gunicorn app:app)
usms/
  __init__.py           App factory, blueprint registration
  config.py             Config from environment variables
  extensions.py         db, migrate, login manager, CSRF
  models.py             SQLAlchemy models: User, Company, Internship, LogEntry, LeaveRequest, Attendance, ActivityLog
  access.py             All role/permission rules + activity logging
  cli.py                flask create-admin, flask seed-demo
  forms.py              Small form-parsing helpers
  blueprints/
    auth.py             /login, /logout, /password
    admin.py            /admin/...   (admin only)
    staff.py            /staff/...   (professors, HR, admins)
    student.py          /me/...      (students)
  templates/            Jinja templates, one folder per blueprint
  static/style.css      Plain CSS, no build step
migrations/             Alembic migrations
tests/                  pytest suite
```

**Key idea:** an `Internship` links one student to one company with a start and an end date.
A student's history is the list of their internships, and logs, attendance and leave all belong to an internship.
That's how HR access is scoped: HR sees only internships at their own company.

## Contributing

PRs are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](codeofconduct.md).

## License

[MIT](LICENCE.md)
