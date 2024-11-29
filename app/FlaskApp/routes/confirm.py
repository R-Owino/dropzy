from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   session)
from cognito import confirm_user, resend_verification_code

confirm_bp = Blueprint("confirm", __name__)

@confirm_bp.route("/confirm", methods=["GET", "POST"])
def confirm():
    """defines a route for user email verification"""
    email = session.get("verification_email")
    if not email:
        flash("No email to verify. Please register first.", "warning")
        return redirect(url_for("register.register"))
    if request.method == "POST":
        if "resend" in request.form:
            # resend verification code
            result = resend_verification_code(email)
            if result["success"]:
                flash("Verification code resent. Check your email.", "info")
            else:
                flash(result["message"], "danger")
        else:
            # confirm the user
            code = request.form.get("code")
            result = confirm_user(email, code)
            if result["success"]:
                flash("Email verified successfully! Please log in.", "success")
                session.pop("verification_email", None)
                return redirect(url_for("login.login"))
            else:
                flash(result["message"], "danger")
        
        return render_template("confirm.html")
