import os

os.environ.setdefault('FLASK_ENV', 'testing')

from app import create_app


def test_create_app_returns_flask_app():
    app = create_app()
    assert app is not None


def test_login_page_loads():
    app = create_app()
    client = app.test_client()
    response = client.get('/auth/login')
    assert response.status_code == 200
