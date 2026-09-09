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


def test_home_redirects_admin_to_admin_dashboard():
    app = create_app()
    client = app.test_client()
    with client.session_transaction() as session:
        session['user'] = {'user_id': 1, 'name': 'Admin One', 'email': 'admin@example.com', 'role': 'admin'}

    response = client.get('/')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/admin/dashboard')
