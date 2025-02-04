from flask import (Blueprint,
                   redirect,
                   url_for,
                   session)

logout_bp = Blueprint("logout", __name__)


@logout_bp.route("/logout")
def logout():
    """defines the logout route"""
    session.clear()
    return redirect(url_for("login.login"))
