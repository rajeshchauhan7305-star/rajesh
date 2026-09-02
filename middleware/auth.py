from functools import wraps

from flask import redirect, session, url_for


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth_login'))
        return f(*args, **kwargs)
    return wrapper


def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('auth_login'))
            if session['user']['role'] != role:
                return redirect(url_for('unauthorized'))
            return f(*args, **kwargs)
        return wrapper
    return decorator
