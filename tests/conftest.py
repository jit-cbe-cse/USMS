import pytest

from usms import create_app
from usms.config import TestConfig
from usms.extensions import db


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        app.test_cli_runner().invoke(args=["seed-demo"])
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def login(client):
    def _login(email, password="password"):
        client.post("/logout")
        return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)
    return _login
