from functools import wraps
from flask import redirect, url_for, flash
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                if claims.get('rol') not in roles:
                    flash("No tienes permiso para acceder a esta página", "danger")
                    return redirect(url_for('home'))
            except Exception:
                flash("Token inválido o expirado", "danger")
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated
    return wrapper
