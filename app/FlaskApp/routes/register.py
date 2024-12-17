from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   session)
from cognito import register_user

register_bp = Blueprint("register", __name__)

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    """defines the register route"""
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        result = register_user(email, username, password)
        if result["Success"]:
            flash("Registration Successful! Please verify your email.", "success")
            session["verification_email"] = email
            return redirect(url_for("confirm.confirm"))
        else:
            flash(result["message"], "danger")
    
    return render_template("register.html")
