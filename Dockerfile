FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 FLASK_APP=app.py
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN useradd --create-home usms && mkdir -p instance && chown -R usms /app
USER usms

EXPOSE 8000
# Apply pending migrations, then serve.
CMD ["sh", "-c", "flask db upgrade && gunicorn -w 3 -b 0.0.0.0:8000 app:app"]
