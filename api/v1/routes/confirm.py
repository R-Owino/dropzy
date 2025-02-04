from flask import (Blueprint,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   session,
                   jsonify)
from cognito import confirm_user
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

confirm_bp = Blueprint("confirm", __name__)


@confirm_bp.route("/confirm", methods=["GET", "POST"])
def confirm():
    """defines a route for user email verification"""

    email = session.get("verification_email")
    if not email:
        return redirect(url_for("register.register"))

    if request.method == "POST":
        code = request.form.get("code")
        if not code:
            return render_template("confirm.html")

        code = code.replace(" ", "")

        result = confirm_user(email, code)
        if result.get("Success") or "CONFIRMED" in result.get("message", ""):
            logger.info(
                f"User {email} verified successfully or already confirmed"
            )
            session.pop("verification_email", None)

            if request.headers.get('Accept') == 'application/json':
                return jsonify({
                    "success": True,
                    "redirect_url": url_for("login.login")
                }), 200
            else:
                return redirect(url_for("login.login")), 302
        else:
            logger.warning(
                f"Verification failed for {email}: {result.get('message')}"
            )
            return jsonify({
                "success": False,
                "message": result.get(
                    "message", "Verification failed. Please try again.")
            })

    return render_template("confirm.html")
