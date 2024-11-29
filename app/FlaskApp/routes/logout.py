from flask import (Blueprint,
                   redirect,
                   url_for,
                   flash,
                   session)

logout_bp = Blueprint("logout", __name__)

@logout_bp.route("/logout")
def logout():
    """defines the logout route"""
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login.login"))
