from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('role'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('role')
            if not user_role:
                return redirect(url_for('auth.login'))
            if user_role not in roles:
                flash('Akses ditolak! Anda tidak memiliki wewenang untuk halaman ini.', 'danger')
                if user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user_role == 'guru':
                    return redirect(url_for('guru.dashboard'))
                elif user_role == 'ortu':
                    return redirect(url_for('ortu.dashboard'))
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
