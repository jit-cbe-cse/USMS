# Contributing to USMS

Thanks for helping! This guide gets you from zero to an open pull request.

## 1. Set up

Follow **Quick start** in the [README](README.md). The key steps are:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env        # local config; the defaults use SQLite, so no database server is needed
flask db upgrade && flask seed-demo
flask run
```

 You should be able to run `flask run`, log in as a demo user and run `pytest` with every test passing.

## 2. Pick something

- Browse issues labelled `good first issue` or `help wanted`.
- Larger features are listed in [docs/ROADMAP.md](docs/ROADMAP.md). Please open an issue to discuss the design before starting one.
- Comment on the issue so nobody duplicates your work.

## 3. Branch and code

```bash
git checkout -b feature/short-description   # or fix/..., docs/...
```

Guidelines:

- **Permissions go in `usms/access.py`.** Views should call `roles_required(...)` and the `visible_*` / `can_*` helpers rather than hand-rolling checks. Any new data must be scoped per role (HR sees their company only, students see only themselves).
- **Schema changes need a migration.** Edit `usms/models.py`, run `flask db migrate -m "..."`, review the generated file and commit it. Keep it working on both SQLite and MySQL: give every `String` column a length, and avoid DB-specific SQL.
- **Every POST form** must include the CSRF token (`{{ csrf() }}` from `_macros.html`).
- **Log meaningful actions** with `record_activity("action_name", "details")` so admins can see them.
- **Configuration goes through environment variables.** Read new settings in `usms/config.py` with a safe dev default,
  then document them in `.env.example` (with a comment) and the README's Configuration table.
  Never hard-code secrets, and never commit `.env`.
- Keep the UI simple: server-rendered Jinja and `static/style.css`, no JS build step.
- Follow PEP 8 and keep lines under 120 characters.

## 4. Test

Add tests in `tests/` for new behaviour, especially permission rules: test both who *can* and who *cannot* do something.

```bash
pytest
```

## 5. Commit and open a PR

- Write clear commit messages ("Add document request model and HR view").
- Open the PR against `main` and describe what changed, why, and how you tested it. Include screenshots for UI changes.
- Double-check that `git status` doesn't list `.env`, `instance/` or any database files.
- CI runs the test suite on every PR, and it must pass.
- A maintainer will review it. Please be patient and responsive to feedback.

## License of contributions

USMS is licensed under [AGPL-3.0](LICENSE). By opening a pull request, you agree that your contribution is licensed under the same terms.

## Reporting bugs

Open an issue with steps to reproduce, expected vs. actual behaviour, and your environment (OS, Python version, SQLite or MySQL).
For security issues, **do not open a public issue**: contact the maintainers privately.
