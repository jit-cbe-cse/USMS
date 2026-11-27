# Roadmap

## ✅ Phase 1: Core (done)
- Login with four roles (Admin, Professor, Company HR/Manager, Student) and role-scoped access
- Companies and users managed by admins
- Internships: students assigned to companies with dates; full history per student
- Student daily logs (create and edit), visible to professors and the company's HR
- Daily attendance check-in; attendance view for staff
- Leave requests: students request, HR approves or denies, professors view
- Admin activity log (logins and all write actions)
- SQLite (dev) / MySQL (prod), Alembic migrations, Docker Compose, pytest suite

## Phase 2: Documents
- [ ] HR requests documents from interns; students upload them; documentation history for students
- [ ] Certificate and offer-letter templates uploaded by HR, with placeholders (`{{student_name}}`, dates, ...)
- [ ] Generate PDFs from templates (e.g. WeasyPrint) for download and printing
- [ ] Email documents to students and professors (Flask-Mail / SMTP)
- [ ] Professors can view certificates and offer letters per student

## Phase 3: Company workspace
- [ ] Company-specific resources (links, files) visible only to current interns
- [ ] Internship feedback forms (HR → professor, student → college)
- [ ] HR manages interns: edit details, end internships, mark absences

## Phase 4: Integrations
- [ ] GitHub / GitLab: link a student's repos and show commit history
- [ ] BookStack: sync or link student logs
- [ ] SSO / college LDAP login (optional)

## Phase 5: Admin and analytics
- [ ] Traffic dashboard (requests per day, active users)
- [ ] Export reports (CSV / PDF) of attendance and internships
- [ ] Password reset by email; bulk CSV import of students
