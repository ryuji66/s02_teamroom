from flask import render_template, session, flash
from functools import wraps



def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("会員登録を行わないと使用できない機能です")
            return render_template("login.html")
        return f(*args, **kwargs)
    return decorated_function