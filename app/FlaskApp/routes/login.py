from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   session)
from cognito import login_user

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["GET", "POST"])
def login():
    """defines the login route"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        result = login_user(username, password)
        if result["success"]:
            session["username"] = username
            session["access_token"] = result["tokens"]["AccessToken"]
            flash("Login Successful!", "success")
            return redirect(url_for("main.main"))
        else:
            flash(result["message"], "danger")
    
    return render_template("login.html")
