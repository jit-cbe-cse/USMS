# Roadmap

Every item below is a GitHub issue. Pick one, comment on it to claim it, and see [CONTRIBUTING.md](../CONTRIBUTING.md).
New here? Start with [`good first issue`](https://github.com/jit-cbe-cse/USMS/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).
Track progress on the [milestones page](https://github.com/jit-cbe-cse/USMS/milestones).

## ✅ Phase 1: Core (done, #1)
- Login with four roles (Admin, Professor, Company HR/Manager, Student) and role-scoped access
- Companies and users managed by admins
- Internships: students assigned to companies with dates; full history per student
- Student daily logs (create and edit), visible to professors and the company's HR
- Daily attendance check-in; attendance view for staff
- Leave requests: students request, HR approves or denies, professors view
- Admin activity log (logins and all write actions)
- SQLite (dev) / MySQL (prod), Alembic migrations, Docker Compose, pytest suite

## Phase 1b: Core follow-ups
Milestone: [Basic layout and functions](https://github.com/jit-cbe-cse/USMS/milestone/1)

- [ ] [#2](https://github.com/jit-cbe-cse/USMS/issues/2) Docs: note macOS port 5000 conflict (AirPlay) and use --port 5001
- [ ] [#3](https://github.com/jit-cbe-cse/USMS/issues/3) Password reset via email (forgot password)
- [ ] [#4](https://github.com/jit-cbe-cse/USMS/issues/4) HR/Admin: edit intern internship details and remove an internship
- [ ] [#5](https://github.com/jit-cbe-cse/USMS/issues/5) HR marks absence/leave; approved leave auto-fills attendance
- [ ] [#6](https://github.com/jit-cbe-cse/USMS/issues/6) Attendance report per internship with date filter
- [ ] [#7](https://github.com/jit-cbe-cse/USMS/issues/7) Student profile: edit name, phone, department, year
- [ ] [#8](https://github.com/jit-cbe-cse/USMS/issues/8) Assign a faculty mentor (professor) to a student
- [ ] [#9](https://github.com/jit-cbe-cse/USMS/issues/9) Bulk import students from CSV
- [ ] [#10](https://github.com/jit-cbe-cse/USMS/issues/10) Pagination and search on Students, Leave requests and Logs lists
- [ ] [#11](https://github.com/jit-cbe-cse/USMS/issues/11) Responsive layout for header navigation and tables
- [ ] [#12](https://github.com/jit-cbe-cse/USMS/issues/12) Rate-limit login and lock out after repeated failures
- [ ] [#13](https://github.com/jit-cbe-cse/USMS/issues/13) CI: run the test suite against MySQL as well as SQLite
- [ ] [#14](https://github.com/jit-cbe-cse/USMS/issues/14) Publish Docker image to GHCR on release

## Phase 2: Documents & Certificates
Milestone: [Documents & Certificates](https://github.com/jit-cbe-cse/USMS/milestone/2)

- [ ] [#15](https://github.com/jit-cbe-cse/USMS/issues/15) Document model and file storage backend
- [ ] [#16](https://github.com/jit-cbe-cse/USMS/issues/16) HR requests documents from interns; students upload them
- [ ] [#17](https://github.com/jit-cbe-cse/USMS/issues/17) Student: documentation history page
- [ ] [#18](https://github.com/jit-cbe-cse/USMS/issues/18) Certificate and offer-letter templates with placeholders
- [ ] [#19](https://github.com/jit-cbe-cse/USMS/issues/19) Generate PDF certificates and offer letters from templates
- [ ] [#20](https://github.com/jit-cbe-cse/USMS/issues/20) Email documents to students and professors
- [ ] [#21](https://github.com/jit-cbe-cse/USMS/issues/21) Professor view: certificates, offer letters and durations per student

## Phase 3: Company Workspace & Feedback
Milestone: [Company Workspace & Feedback](https://github.com/jit-cbe-cse/USMS/milestone/3)

- [ ] [#22](https://github.com/jit-cbe-cse/USMS/issues/22) Company resources visible only to current interns
- [ ] [#23](https://github.com/jit-cbe-cse/USMS/issues/23) HR internship feedback/evaluation for each student
- [ ] [#24](https://github.com/jit-cbe-cse/USMS/issues/24) Professors view feedback; students give feedback on the company
- [ ] [#25](https://github.com/jit-cbe-cse/USMS/issues/25) Comments on student logs by HR and professors
- [ ] [#26](https://github.com/jit-cbe-cse/USMS/issues/26) Notifications for leave decisions, document requests and comments

## Phase 4: Integrations
Milestone: [Integrations](https://github.com/jit-cbe-cse/USMS/milestone/4)

- [ ] [#27](https://github.com/jit-cbe-cse/USMS/issues/27) Link GitHub/GitLab accounts and repositories to an internship
- [ ] [#28](https://github.com/jit-cbe-cse/USMS/issues/28) Show a student's commit history to HR and professors
- [ ] [#29](https://github.com/jit-cbe-cse/USMS/issues/29) BookStack integration for student logs
- [ ] [#30](https://github.com/jit-cbe-cse/USMS/issues/30) SSO / college LDAP login (optional)

## Phase 5: Admin & Analytics
Milestone: [Admin & Analytics](https://github.com/jit-cbe-cse/USMS/milestone/5)

- [ ] [#31](https://github.com/jit-cbe-cse/USMS/issues/31) Admin: edit/delete companies and users, reassign HR
- [ ] [#32](https://github.com/jit-cbe-cse/USMS/issues/32) Traffic dashboard: requests per day, active users, top pages
- [ ] [#33](https://github.com/jit-cbe-cse/USMS/issues/33) Filter and export the activity log
- [ ] [#34](https://github.com/jit-cbe-cse/USMS/issues/34) Export reports (CSV/PDF) of internships and attendance
