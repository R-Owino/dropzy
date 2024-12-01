from flask import (Blueprint,
                   render_template,
                   redirect,
                   url_for,
                   flash,
                   session)

main_bp = Blueprint("main", __name__)

@main_bp.route("/main")
def main():
    """defines the main page route"""
    if "username" not in session or "email" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login.login"))
    
    return render_template("main.html",
                           username=session["username"],
                           email=session["email"])
