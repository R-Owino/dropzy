from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   session)
from cognito import confirm_user

confirm_bp = Blueprint("confirm", __name__)

@confirm_bp.route("/confirm", methods=["GET", "POST"])
def confirm():
    """defines a route for user email verification"""

    email = session.get("verification_email")
    if not email:
        flash("No email to verify. Please register first.", "warning")
        return redirect(url_for("register.register"))
    
    if request.method == "POST":
        code = request.form.get("code")
        if not code:
            flash("Please enter the verification code.", "danger")
            return render_template("confirm.html")
        
        code = code.replace(" ", "")

        result = confirm_user(email, code)
        if result["Success"]:
            flash("Email verified successfully! Please log in.", "success")
            session.pop("verification_email", None)
            return redirect(url_for("login.login"))
        else:
            flash(result["message"], "danger")
        
    return render_template("confirm.html")
