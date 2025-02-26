from functools import wraps

from flask import abort, redirect, url_for
from flask_login import current_user


def confirmed_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.confirmed:
            return redirect(url_for("auth.unconfirmed"))
        return f(*args, **kwargs)

    return decorated_function


def roles_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator
